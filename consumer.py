import logging
import time
from random import randint
from typing import TYPE_CHECKING

from config import (
    configure_logging,
    MQ_ROUTING_KEY,
    connection_params,
)
from rabbit_p import RabbitBase
from rabbit_p.common import SimpleRabbit

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
    # log.info(
    #     "Channel: %s, Method: %s, Properties:%s, Body: %s",
    #     channel,
    #     method,
    #     properties,
    #     body,
    # )
    log.info("[ ] Received %r", body)
    number = int(body[-2:])
    is_odd = number % 2
    time.sleep(is_odd)
    log.info(
        "[X] Message received: %s -> processing time %.2fs",
        body,
        time.time() - start_time,
    )
    num_random = randint(0, 1)
    if num_random > 0.5:
        log.info(f"Finished un processing message {body} with nack")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        log.info(f"Finished processing message {body} with ack")
        channel.basic_ack(delivery_tag=method.delivery_tag)
    print("-" * 50)


# def consume_message(channel: "BlockingChannel") -> None:
#     channel.basic_qos(prefetch_count=1)
#     channel.queue_declare(queue=MQ_ROUTING_KEY)
#     channel.basic_consume(
#         queue=MQ_ROUTING_KEY,
#         on_message_callback=process_message,
#         # auto_ack=True,
#     )
#     log.warning("Waiting for messages....")
#     channel.start_consuming()


def main():
    configure_logging(level=logging.INFO)
    with SimpleRabbit(connection_params=connection_params) as simple_rabbit:
        simple_rabbit.consume_messages(
            message_callback=process_message,
        )


#
#
# def main():
#     configure_logging(level=logging.INFO)
#     with RabbitBase(connection_params=connection_params) as rabbit:
#         consume_message(
#             channel=rabbit.channel,
#         )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info(
            "Stopping publisher",
        )
