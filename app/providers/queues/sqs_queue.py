"""AWS SQS queue provider."""

import json
from typing import Any

from botocore.exceptions import ClientError, NoCredentialsError

from app.config.settings import Settings
from app.logger import logger
from app.providers.clients.aws_boto import get_boto_client
from app.providers.queues.base import QueueProvider
from app.providers.queues.exceptions import QueueDeleteError, QueueReceiveError, QueueSendError


class SQSQueue(QueueProvider):
    """AWS SQS queue implementation."""

    def __init__(
        self,
        settings: Settings,
        queue_name: str | None = None,
    ):
        """
        Initialize SQS queue.

        Args:
            settings: Application settings
            queue_name: Name of the SQS queue (overrides settings default)
        """
        self.queue_name = queue_name or settings.aws_sqs_queue_name
        self.region = settings.aws_region
        self.settings = settings

    def initialize(self) -> "SQSQueue":
        """SQSQueue does not require async initialization."""
        if self.settings.mode.lower() in ["staging", "production", "development"]:
            try:
                self.sqs_client = get_boto_client("sqs", region_name=self.region)
                self.queue_url = self.sqs_client.get_queue_url(QueueName=self.queue_name)[
                    "QueueUrl"
                ]
                logger.info(
                    "SQSQueue initialized",
                    queue_name=self.queue_name,
                    queueUrl=self.queue_url,
                    region=self.region,
                )
                return self

            except NoCredentialsError as e:
                logger.error("AWS credentials not configured", error=str(e))

            except ClientError as e:
                logger.error("Failed to initialize SQSQueue", error=str(e))
        self.queue_url = None
        self.sqs_client = None
        return self

    async def send_message(
        self,
        message_body: str | dict[str, Any],
        delay_seconds: int = 0,
        message_attributes: dict[str, Any] | None = None,
    ) -> str:
        """
        Send a message to the SQS queue.

        Args:
            message_body: Message content (string or dict that will be JSON serialized)
            delay_seconds: Delay before message becomes available (0-900 seconds)
            message_attributes: Optional message attributes/metadata

        Returns:
            Message ID of the sent message

        Raises:
            QueueSendError: If sending fails
        """
        if self.sqs_client is None:
            raise QueueSendError(
                f"SQS client not initialized, cannot send message in {self.settings.mode} mode"
            )

        try:
            if isinstance(message_body, dict):
                message_body = json.dumps(message_body)

            params = {
                "QueueUrl": self.queue_url,
                "MessageBody": message_body,
                "DelaySeconds": delay_seconds,
            }

            if message_attributes:
                params["MessageAttributes"] = self._format_message_attributes(message_attributes)

            response = self.sqs_client.send_message(**params)
            message_id = response["MessageId"]

            logger.info(
                "Message sent to SQS",
                message_id=message_id,
                queue_name=self.queue_name,
            )
            return message_id

        except ClientError as e:
            logger.error("Failed to send message to SQS", error=str(e))
            raise QueueSendError(f"Failed to send message: {e}") from e

    async def receive_messages(
        self,
        max_messages: int = 1,
        wait_time_seconds: int = 0,
        visibility_timeout: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Receive messages from the SQS queue.

        Args:
            max_messages: Maximum number of messages to retrieve (1-10)
            wait_time_seconds: Long polling wait time (0-20 seconds)
            visibility_timeout: Time the message is hidden from other consumers (0-43200 seconds)

        Returns:
            List of messages with their metadata

        Raises:
            QueueReceiveError: If receiving fails
        """
        if self.sqs_client is None:
            logger.warning(
                "SQS client not initialized, returning empty message list",
                mode=self.settings.mode,
            )
            return []

        try:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=min(max_messages, 10),  # AWS limit is 10
                WaitTimeSeconds=min(wait_time_seconds, 20),  # AWS limit is 20
                VisibilityTimeout=visibility_timeout,
                MessageAttributeNames=["All"],
            )

            messages = response.get("Messages", [])
            logger.info(
                f"Received {len(messages)} message(s) from SQS",
                queue_name=self.queue_name,
            )

            # Parse JSON message bodies if possible
            for message in messages:
                try:
                    message["ParsedBody"] = json.loads(message["Body"])
                except json.JSONDecodeError:
                    message["ParsedBody"] = message["Body"]

            return messages

        except ClientError as e:
            logger.error("Failed to receive messages from SQS", error=str(e))
            raise QueueReceiveError(f"Failed to receive messages: {e}") from e

    async def delete_message(self, receipt_handle: str) -> bool:
        """
        Delete a message from the SQS queue.

        Args:
            receipt_handle: Receipt handle from received message

        Returns:
            True if deletion was successful

        Raises:
            QueueDeleteError: If deletion fails
        """
        if self.sqs_client is None:
            logger.warning(
                "SQS client not initialized, skipping message deletion",
                mode=self.settings.mode,
            )
            return True

        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )

            logger.info("Message deleted from SQS", queue_name=self.queue_name)
            return True

        except ClientError as e:
            logger.error("Failed to delete message from SQS", error=str(e))
            raise QueueDeleteError(f"Failed to delete message: {e}") from e

    def _format_message_attributes(self, attributes: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """
        Format message attributes for SQS.

        Args:
            attributes: Dictionary of attributes

        Returns:
            Formatted attributes for SQS
        """
        formatted = {}
        for key, value in attributes.items():
            if isinstance(value, str):
                formatted[key] = {"DataType": "String", "StringValue": value}
            elif isinstance(value, (int, float)):
                formatted[key] = {"DataType": "Number", "StringValue": str(value)}
            elif isinstance(value, bytes):
                formatted[key] = {"DataType": "Binary", "BinaryValue": value}
            else:
                # Default to string for other types
                formatted[key] = {"DataType": "String", "StringValue": str(value)}

        return formatted
