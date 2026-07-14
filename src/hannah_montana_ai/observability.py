import json
import logging
import threading
import time
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "HTTP requests handled by Hannah Montana AI",
    ("method", "path", "status"),
)
HTTP_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency for Hannah Montana AI",
    ("method", "path"),
)
ERROR_LOGS = Counter(
    "application_log_events_total",
    "Application log events emitted by Hannah Montana AI",
    ("level",),
)
BUSINESS_EVENTS = Counter(
    "business_events_total",
    "Business events emitted by Hannah Montana AI",
    ("service", "type"),
)
DISCORD_NOTIFICATIONS = Counter(
    "discord_notifications_total",
    "Discord notification delivery results",
    ("service", "result"),
)

logger = logging.getLogger(__name__)


class ErrorMetricHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno >= logging.ERROR:
            ERROR_LOGS.labels(level="error").inc()


class DiscordBusinessNotifier:
    def __init__(self, webhook_url: str, runtime_environment: str) -> None:
        if runtime_environment not in {"local", "production"}:
            raise RuntimeError("HANNAH_RUNTIME_ENVIRONMENT must be local or production")
        self._webhook_url = webhook_url.strip()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="hannah-discord")
        self._capacity = threading.BoundedSemaphore(500)
        if not self._webhook_url:
            if runtime_environment == "production":
                raise RuntimeError("HANNAH_DISCORD_WEBHOOK_URL is required in production")
            return
        parsed = urllib.parse.urlparse(self._webhook_url)
        if (
            parsed.scheme != "https"
            or parsed.hostname != "discord.com"
            or not parsed.path.startswith("/api/webhooks/")
        ):
            raise RuntimeError("HANNAH_DISCORD_WEBHOOK_URL must be an HTTPS Discord webhook URL")

    def publish(self, event_type: str, title: str, details: dict[str, str]) -> None:
        BUSINESS_EVENTS.labels(service="hannah-ai", type=event_type).inc()
        if not self._webhook_url:
            DISCORD_NOTIFICATIONS.labels(service="hannah-ai", result="not_configured").inc()
            return
        if not self._capacity.acquire(blocking=False):
            DISCORD_NOTIFICATIONS.labels(service="hannah-ai", result="queue_rejected").inc()
            logger.error("Discord business notification queue rejected event type=%s", event_type)
            return
        event_id = str(uuid.uuid4())
        future = self._executor.submit(self._send, event_id, event_type, title, details)
        future.add_done_callback(lambda _future: self._capacity.release())

    def _send(
        self,
        event_id: str,
        event_type: str,
        title: str,
        details: dict[str, str],
    ) -> None:
        fields = [
            {"name": key[:256], "value": value[:500], "inline": True}
            for key, value in details.items()
        ]
        body = json.dumps(
            {
                "username": "Hana Montana AI",
                "allowed_mentions": {"parse": []},
                "embeds": [
                    {
                        "title": title[:256],
                        "description": f"event={event_type} id={event_id}",
                        "color": 0x008485,
                        "fields": fields,
                    }
                ],
            }
        ).encode()
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                request = urllib.request.Request(  # noqa: S310  # nosec B310
                    self._webhook_url,
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(  # noqa: S310  # nosec B310
                    request, timeout=5.0
                ) as response:
                    if 200 <= response.status < 300:
                        DISCORD_NOTIFICATIONS.labels(service="hannah-ai", result="sent").inc()
                        return
                    last_error = RuntimeError(f"Discord returned HTTP {response.status}")
            except Exception as exception:
                last_error = exception
            if attempt < 3:
                time.sleep(0.25 * attempt)
        DISCORD_NOTIFICATIONS.labels(service="hannah-ai", result="send_failed").inc()
        logger.error(
            "Discord business notification failed type=%s eventId=%s",
            event_type,
            event_id,
            exc_info=last_error,
        )


_notifier: DiscordBusinessNotifier | None = None
_logging_configured = False


def configure_observability(webhook_url: str, runtime_environment: str) -> None:
    global _logging_configured, _notifier
    if not _logging_configured:
        logging.getLogger().addHandler(ErrorMetricHandler())
        _logging_configured = True
    _notifier = DiscordBusinessNotifier(webhook_url, runtime_environment)


def publish_business_event(event_type: str, title: str, details: dict[str, Any]) -> None:
    if _notifier is None:
        raise RuntimeError("Observability has not been configured")
    _notifier.publish(event_type, title, {key: str(value) for key, value in details.items()})
