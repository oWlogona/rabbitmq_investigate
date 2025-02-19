import logging
import time
from typing import TYPE_CHECKING

from config import (
    get_connection,
    configure_logging,
    MQ_ROUTING_KEY,
    MQ_EXCHANGE,
    connection_params,
)
from rabbit_p.common import SimpleRabbit


log = logging.getLogger(__name__)
if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel


class Publisher(SimpleRabbit):
    def produce_message(self, idx: int) -> None:
        message_body = f"Message #{idx:02d}"
        log.warning("Publish message: %s", message_body)
        self.channel.basic_publish(
            exchange=MQ_EXCHANGE,
            routing_key=MQ_ROUTING_KEY,
            body=message_body,
        )
        log.warning("Published message: %s", message_body)


# def declare_queue(channel: "BlockingChannel") -> None:
#     queue = channel.queue_declare(queue=MQ_ROUTING_KEY)
#     log.warning(
#         "Declaring queue: %s, routing key: %s",
#         queue,
#         MQ_ROUTING_KEY,
#     )


# def produce_message(channel: "BlockingChannel", idx: int) -> None:
#     message_body = f"Message #{idx:02d}"
#     log.warning("Publish message: %s", message_body)
#     channel.basic_publish(
#         exchange=MQ_EXCHANGE,
#         routing_key=MQ_ROUTING_KEY,
#         body=message_body,
#     )
#     log.warning("Published message: %s", message_body)


def main():
    configure_logging(level=logging.WARNING)
    with Publisher(connection_params=connection_params) as publisher:
        publisher.declare_queue()
        for idx in range(1, 11):
            publisher.produce_message(
                idx=idx,
            )


# def main():
#     configure_logging(level=logging.WARNING)
#     with get_connection() as connection:
#         log.warning("Starting publisher %s", connection)
#         with connection.channel() as channel_object:
#             log.warning("Starting channel %s", channel_object)
#             declare_queue(channel=channel_object)
#             for idx in range(1, 11):
#                 produce_message(
#                     channel=channel_object,
#                     idx=idx,
#                 )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info(
            "Stopping publisher",
        )
