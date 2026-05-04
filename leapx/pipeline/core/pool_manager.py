"""Worker pool management."""

import asyncio
import os
from collections.abc import Callable, Coroutine
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any


class PoolManager:
    """Manages CPU/IO worker pools and concurrency limits.

    Creates and reuses process and thread pools for CPU- and IO-bound work,
    and provides helpers to run coroutines with an LLM concurrency semaphore.

    Args:
        cpu_workers: Max number of processes for CPU-bound tasks.
        Defaults to os.cpu_count().
        io_workers: Max number of threads for IO-bound tasks.
        max_concurrent_llm_calls: Max concurrent LLM calls guarded by a semaphore.
    """

    def __init__(
        self,
        cpu_workers: int | None = 0,
        io_workers: int = 20,
        max_concurrent_llm_calls: int = 2,
    ):
        self._cpu_workers = os.cpu_count() if cpu_workers is None else cpu_workers
        self._io_workers = io_workers
        self._cpu_pool: ProcessPoolExecutor | None = None
        self._io_pool: ThreadPoolExecutor | None = None
        self._max_concurrent_llm_calls = max_concurrent_llm_calls
        self._llm_semaphore: asyncio.Semaphore | None = None

    def _get_llm_semaphore(self) -> asyncio.Semaphore:
        """Get or create the LLM semaphore for the current event loop.

        Returns:
            asyncio.Semaphore limiting concurrent LLM calls.
        """
        if self._llm_semaphore is None:
            self._llm_semaphore = asyncio.Semaphore(self._max_concurrent_llm_calls)
        return self._llm_semaphore

    def _ensure_pools(self) -> None:
        """Ensure process and thread pools are initialized."""
        if self._cpu_pool is None and self._cpu_workers > 0:
            self._cpu_pool = ProcessPoolExecutor(max_workers=self._cpu_workers)
        if self._io_pool is None:
            self._io_pool = ThreadPoolExecutor(max_workers=self._io_workers)

    async def run_cpu(self, fn: Callable, *args) -> Any:
        """Run a CPU-bound synchronous function in the process pool.

        Args:
            fn: Callable to execute.
            *args: Arguments passed to the callable.

        Returns:
            The callable's return value.
        """
        self._ensure_pools()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._cpu_pool, fn, *args)

    async def run_io(self, fn: Callable, *args) -> Any:
        """Run an IO-bound synchronous function in the thread pool.

        Args:
            fn: Callable to execute.
            *args: Arguments passed to the callable.

        Returns:
            The callable's return value.
        """
        self._ensure_pools()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._io_pool, fn, *args)

    async def run_with_llm_limit(self, coro: Coroutine[Any, Any, Any]) -> Any:
        """Run a coroutine with the LLM concurrency limit applied.

        Args:
            coro: Awaitable representing an LLM call.

        Returns:
            Result of the awaited coroutine.
        """
        async with self._get_llm_semaphore():
            return await coro

    async def run_concurrently(
        self, tasks: list[Coroutine[Any, Any, Any]]
    ) -> list[Any]:
        """Run multiple coroutines in parallel and gather results.

        Args:
            tasks: List of awaitables to execute concurrently.

        Returns:
            List of results in the same order as the input tasks.
        """
        return await asyncio.gather(*tasks)

    async def run_in_concurrent_processes(
        self, fn: Callable, args_list: list[tuple]
    ) -> list[Any]:
        """Run a function for multiple argument sets using the IO thread pool.

        Note: Despite the name, this uses the IO thread pool to dispatch work
        that itself may start a process loop (e.g., creating new event loops).

        Args:
            fn: A function to run for each argument tuple.
            args_list: List of argument tuples.

        Returns:
            List of results from each execution.
        """
        self._ensure_pools()
        loop = asyncio.get_running_loop()

        futures = [loop.run_in_executor(self._io_pool, fn, *args) for args in args_list]
        return await asyncio.gather(*futures)

    async def close(self) -> None:
        """Shutdown and cleanup internal executors."""
        if self._cpu_pool:
            self._cpu_pool.shutdown(wait=True)
            self._cpu_pool = None
        if self._io_pool:
            self._io_pool.shutdown(wait=True)
            self._io_pool = None
