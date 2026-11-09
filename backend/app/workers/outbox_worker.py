"""Standalone background worker executing transactional outbox events."""

import logging
import os
import signal
import sys
import time
from typing import Optional

from app.services.outbox_consumer import OutboxConsumer, get_outbox_consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("outbox_worker")


class OutboxWorkerRunner:
    """Manages the lifecycle, signal handling, and execution loop of the outbox consumer worker."""

    def __init__(
        self,
        consumer: Optional[OutboxConsumer] = None,
        poll_interval: float = 2.0,
        batch_size: int = 10,
    ):
        self.consumer = consumer or get_outbox_consumer()
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self._running = True

    def stop(self, *args, **kwargs) -> None:
        """Signal callback to gracefully stop the loop."""
        logger.info("Shutdown signal received. Stopping outbox worker gracefully...")
        self._running = False

    def run(self) -> None:
        """Run the main worker polling loop."""
        logger.info(
            f"Starting PayPilot Outbox Worker (poll_interval={self.poll_interval}s, batch_size={self.batch_size})"
        )

        # Register signals for graceful termination
        try:
            signal.signal(signal.SIGINT, self.stop)
            signal.signal(signal.SIGTERM, self.stop)
        except (ValueError, AttributeError):
            # In non-main thread or certain OS contexts
            pass

        consecutive_idle = 0
        while self._running:
            try:
                processed_count = self.consumer.process_batch(batch_size=self.batch_size)
                if processed_count > 0:
                    logger.info(f"Successfully processed {processed_count} outbox event(s).")
                    consecutive_idle = 0
                    # If we processed a full batch, check immediately without sleeping
                    if processed_count >= self.batch_size:
                        continue
                else:
                    consecutive_idle += 1

                # Sleep interval
                time.sleep(self.poll_interval)
            except Exception as exc:
                logger.error(f"Unexpected error in outbox worker loop: {exc}", exc_info=True)
                time.sleep(self.poll_interval)

        logger.info("PayPilot Outbox Worker terminated cleanly.")


def main():
    poll_interval = float(os.getenv("OUTBOX_POLL_INTERVAL", "2.0"))
    batch_size = int(os.getenv("OUTBOX_BATCH_SIZE", "10"))
    runner = OutboxWorkerRunner(poll_interval=poll_interval, batch_size=batch_size)
    runner.run()


if __name__ == "__main__":
    main()

