from typing import TYPE_CHECKING, Callable

import config
from config import MQ_EMAIL_UPDATES_EXCHANGE
import logging

from rabbit_p import RabbitBase

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


class SimpleRabbitMixin:
    channel: "BlockingChannel"

    def declare_queue(self) -> None:
        self.channel.exchange_declare(
            exchange=config.MQ_QUEUE_NAME_DEAD_LETTER_EXCHANGE,
            exchange_type="fanout",
        )
        dlq = self.channel.queue_declare(
            queue=config.MQ_QUEUE_NAME_DEAD_LETTER_KEY,
        )
        self.channel.queue_bind(
            queue=dlq.method.queue,
            exchange=config.MQ_QUEUE_NAME_DEAD_LETTER_EXCHANGE,
        )
        log.info(f"Declaring queue: {dlq.method.queue}")
        queue = self.channel.queue_declare(
            queue=config.MQ_ROUTING_KEY,
            arguments={
                "x-dead-letter-exchange": config.MQ_QUEUE_NAME_DEAD_LETTER_EXCHANGE,
                # "x-dead-letter-routing-key": config.MQ_QUEUE_NAME_DEAD_LETTER_KEY,
            },
        )
        log.info(f"Declaring queue: {queue.method.queue}")

    def consume_messages(
        self,
        message_callback: Callable[
            [
                "BlockingChannel",
                "Basic.Deliver",
                "BasicProperties",
                bytes,
            ],
            None,
        ],
        queue_name: str = "",
        prefetch_count: int = 1,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.declare_queue()
        self.channel.basic_consume(
            queue=config.MQ_ROUTING_KEY,
            on_message_callback=message_callback,
            # auto_ack=True,
        )
        log.warning("Waiting for messages....")
        self.channel.start_consuming()


class SimpleRabbit(SimpleRabbitMixin, RabbitBase):
    pass
