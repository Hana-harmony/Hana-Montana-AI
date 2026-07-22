import asyncio
import threading

from hannah_montana_ai.runtime_workloads import TaxOcrExecutor


def test_tax_ocr_executor_uses_dedicated_threads() -> None:
    executor = TaxOcrExecutor(max_workers=1)

    async def run() -> str:
        return await executor.run(lambda: threading.current_thread().name)

    try:
        thread_name = asyncio.run(run())
    finally:
        executor.shutdown()

    assert thread_name.startswith("hannah-tax-ocr")


def test_tax_ocr_executor_can_restart_after_shutdown() -> None:
    executor = TaxOcrExecutor(max_workers=1)

    async def run() -> int:
        return await executor.run(lambda: 7)

    assert asyncio.run(run()) == 7
    executor.shutdown()
    assert asyncio.run(run()) == 7
    executor.shutdown()
