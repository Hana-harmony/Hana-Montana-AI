from __future__ import annotations

import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore, Lock
from typing import TypeVar

T = TypeVar("T")


class TaxOcrExecutor:
    """뉴스 분석과 분리된 실행 풀에서 세무 OCR을 처리한다."""

    def __init__(self, max_workers: int = 2) -> None:
        self._max_workers = max_workers
        self._lock = Lock()
        self._executor: ThreadPoolExecutor | None = None

    async def run(self, operation: Callable[[], T]) -> T:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._current_executor(), operation)

    def shutdown(self) -> None:
        with self._lock:
            executor = self._executor
            self._executor = None
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=False)

    def _current_executor(self) -> ThreadPoolExecutor:
        with self._lock:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=self._max_workers,
                    thread_name_prefix="hannah-tax-ocr",
                )
            return self._executor


# 번역 모델의 실질 동시 처리량에 맞춰 CPU 추론 과다 병렬화를 막는다.
alert_analysis_capacity = BoundedSemaphore(value=1)
tax_ocr_executor = TaxOcrExecutor(max_workers=2)
