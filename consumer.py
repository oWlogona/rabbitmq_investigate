import logging
import time
from typing import TYPE_CHECKING

from config import get_connection, configure_logging, MQ_ROUTING_KEY, MQ_EXCHANGE

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
    log.info(
        "Channel: %s, Method: %s, Properties:%s, Body: %s",
        channel,
        method,
        properties,
        body,
    )
    log.warning("[ ] Received %r", body)
    number = int(body[-2:])
    is_odd = number % 2
    print(is_odd)
    time.sleep(1 + is_odd + 1)
    log.warning(
        "[X] Message received: %s -> processing time %.2fs",
        body,
        time.time() - start_time,
    )
    channel.basic_ack(delivery_tag=method.delivery_tag)


def consume_message(channel: "BlockingChannel") -> None:
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=MQ_ROUTING_KEY,
        on_message_callback=process_message,
        # auto_ack=True,
    )
    log.warning("Waiting for messages....")
    channel.start_consuming()


def main():
    configure_logging(level=logging.WARNING)
    with get_connection() as connection:
        log.info("Starting publisher %s", connection)
        with connection.channel() as channel_object:
            log.info("Starting channel %s", channel_object)
            consume_message(
                channel=channel_object,
            )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info(
            "Stopping publisher",
        )
