import logging
import time
from typing import TYPE_CHECKING

from config import (
    get_connection,
    configure_logging,
    MQ_ROUTING_KEY,
    MQ_EXCHANGE,
    connection_params,
    MQ_QUEUE_NAME_KYC_EMAIL_UPDATE,
)
from rabbit_p import RabbitBase
from rabbit_p.common import EmailUpdatesRabbit

log = logging.getLogger(__name__)
if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


def process_message(
    channel: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
):
    start_time = time.time()
    log.warning("[ ] Start checking new user email for bad things %r", body)
    time.sleep(2)
    log.warning(
        "[ ] Finished processing message",
    )
    channel.basic_ack(delivery_tag=method.delivery_tag)

    log.warning(
        "[X] Finished processing message: %s -> processing time %.2fs",
        body,
        time.time() - start_time,
    )


def main():
    configure_logging(level=logging.WARNING)
    with EmailUpdatesRabbit(connection_params=connection_params) as rabbit:
        rabbit.consume_messages(
            message_callback=process_message,
            queue_name=MQ_QUEUE_NAME_KYC_EMAIL_UPDATE,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info(
            "Stopping publisher",
        )
