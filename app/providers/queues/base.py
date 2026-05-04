"""Queue interface for abstracting message queue operations."""

from abc import ABC, abstractmethod
from typing import Any


class QueueProvider(ABC):
    """Abstract interface for queue operations."""

    @abstractmethod
    async def send_message(
        self,
        message_body: str | dict[str, Any],
        delay_seconds: int = 0,
        message_attributes: dict[str, Any] | None = None,
    ) -> str:
        """
        Send a message to the queue.

        Args:
            message_body: Message content (string or dict that will be JSON serialized)
            delay_seconds: Delay before message becomes available (0-900 seconds)
            message_attributes: Optional message attributes/metadata

        Returns:
            Message ID of the sent message
        """

    @abstractmethod
    async def receive_messages(
        self,
        max_messages: int = 1,
        wait_time_seconds: int = 0,
        visibility_timeout: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Receive messages from the queue.

        Args:
            max_messages: Maximum number of messages to retrieve (1-10)
            wait_time_seconds: Long polling wait time (0-20 seconds)
            visibility_timeout: Time the message is hidden from other consumers (0-43200 seconds)

        Returns:
            List of messages with their metadata
        """

    @abstractmethod
    async def delete_message(self, receipt_handle: str) -> bool:
        """
        Delete a message from the queue.

        Args:
            receipt_handle: Receipt handle from received message

        Returns:
            True if deletion was successful
        """
