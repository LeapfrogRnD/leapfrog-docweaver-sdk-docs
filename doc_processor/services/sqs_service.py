"""SQS service to receive messages from AWS SQS queue."""

import asyncio
import json
from collections.abc import Awaitable, Callable

import boto3
from botocore.config import Config
from config.settings import settings
from utils.logger import log


class SQSReceiver:
    """Receive messages from SQS queue."""

    def __init__(self, queue_url: str | None = None):
        self.queue_url = queue_url or settings.SQS_QUEUE_URL
        self.max_messages = settings.SQS_MAX_MESSAGES
        self.wait_time_seconds = settings.SQS_WAIT_TIME_SECONDS
        self.visibility_timeout = settings.SQS_VISIBILITY_TIMEOUT
        self.is_running = False
        self._client = None

        # Configure boto3 with retries
        self._boto_config = Config(
            region_name=settings.AWS_REGION, retries={"max_attempts": 3, "mode": "adaptive"}
        )

    def _get_client(self):
        """Get or create SQS client."""
        if self._client is None:
            client_kwargs = {"config": self._boto_config}
            if settings.SQS_ENDPOINT_URL:
                client_kwargs["endpoint_url"] = settings.SQS_ENDPOINT_URL
            self._client = boto3.client("sqs", **client_kwargs)
        return self._client

    def _close_client(self):
        """Close SQS client."""
        if self._client:
            self._client.close()
            self._client = None

    def resolve_dead_letter_queue_url(self) -> str | None:
        """Resolve DLQ URL from source queue RedrivePolicy or queue-name convention."""
        if not self.queue_url:
            return None

        client = self._get_client()

        # Primary path: derive from queue redrive policy.
        try:
            attrs = client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=["RedrivePolicy"],
            )
            redrive_policy = attrs.get("Attributes", {}).get("RedrivePolicy")
            if redrive_policy:
                policy = json.loads(redrive_policy)
                dlq_arn = policy.get("deadLetterTargetArn")
                if dlq_arn:
                    dlq_name = dlq_arn.rsplit(":", maxsplit=1)[-1]
                    dlq_url_response = client.get_queue_url(QueueName=dlq_name)
                    return dlq_url_response.get("QueueUrl")
        except Exception as e:
            log.warning(f"Could not resolve DLQ from RedrivePolicy: {e}")

        # Fallback path: infer by naming convention, e.g. tasks -> tasks-dlq.
        try:
            queue_name = self.queue_url.rstrip("/").rsplit("/", maxsplit=1)[-1]
            dlq_name = f"{queue_name}{settings.SQS_DLQ_SUFFIX}"
            dlq_url_response = client.get_queue_url(QueueName=dlq_name)
            dlq_url = dlq_url_response.get("QueueUrl")
            if dlq_url:
                log.info(
                    f"Resolved DLQ URL via naming fallback: source={queue_name}, dlq={dlq_name}"
                )
            return dlq_url
        except Exception as e:
            log.error(f"Failed to resolve DLQ URL from queue naming convention: {e}")
            return None

    async def start_receiving(self, message_callback: Callable[[dict, str], Awaitable[None]]):
        """
        Start receiving messages from SQS and call callback for each message.

        Args:
            message_callback: Async function to call with (message_body, receipt_handle)
        """
        if not self.queue_url:
            raise ValueError("SQS_QUEUE_URL is not configured")

        self.is_running = True
        log.info(f"Starting SQS receiver (queue: {self.queue_url})")

        try:
            client = self._get_client()

            while self.is_running:
                try:
                    await self._receive_and_process(client, message_callback)
                except Exception as e:
                    log.error(f"Error in SQS receive loop: {e}")
                    await asyncio.sleep(5)
        finally:
            self._close_client()

    async def _receive_and_process(
        self, client, message_callback: Callable[[dict, str], Awaitable[None]]
    ):
        """Receive messages from SQS and process them."""
        response = await asyncio.to_thread(
            client.receive_message,
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=self.max_messages,
            WaitTimeSeconds=self.wait_time_seconds,
            VisibilityTimeout=self.visibility_timeout,
        )

        messages = response.get("Messages", [])

        if not messages:
            log.debug("No messages received from SQS")
            return

        for message in messages:
            if not self.is_running:
                break

            try:
                body = json.loads(message.get("Body", "{}"))
                receipt_handle = message.get("ReceiptHandle")
                await message_callback(body, receipt_handle)
            except Exception as e:
                log.error(f"Error processing SQS message: {e}")

    async def delete_message(self, receipt_handle: str):
        """Delete a message from the queue."""
        try:
            client = self._get_client()
            await asyncio.to_thread(
                client.delete_message, QueueUrl=self.queue_url, ReceiptHandle=receipt_handle
            )
            log.debug("Deleted SQS message")
        except Exception as e:
            log.error(f"Failed to delete SQS message: {e}")

    def stop_receiving(self):
        """Stop the receive loop."""
        log.info("Stopping SQS receiver...")
        self.is_running = False


# Singleton instance
sqs_receiver = SQSReceiver()
