import logging
import time
from typing import TYPE_CHECKING

import config
from config import (
    configure_logging,
    connection_params,
)
from rabbit_p.common import EmailUpdatesRabbit

log = logging.getLogger(__name__)


class Producer(EmailUpdatesRabbit):

    def produce_message(self, idx: int) -> None:
        message_body = f"Message #{idx:02d}"
        log.warning("Publish message: %s", message_body)
        self.channel.basic_publish(
            exchange=config.MQ_EMAIL_UPDATES_EXCHANGE,
            routing_key="",
            body=message_body,
        )
        log.warning("Published message: %s", message_body)


def main():
    configure_logging(level=logging.WARNING)
    with Producer(connection_params=connection_params) as producer:
        producer.declare_email_updates_exchange()
        for idx in range(1, 34):
            producer.produce_message(
                idx=idx,
            )
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info(
            "Stopping publisher",
        )
