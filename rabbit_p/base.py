import pika
from pika.adapters.blocking_connection import BlockingChannel

from .rabbit_exception import RabbitException


class RabbitBase:
    def __init__(
        self,
        connection_params: pika.ConnectionParameters,
    ):
        self.connection_params = connection_params
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    @property
    def channel(self) -> BlockingChannel | None:
        if self._channel is None:
            raise RabbitException("Please use context manger for Rabbit helper.")
        return self._channel

    def get_connection(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(parameters=self.connection_params)

    def __enter__(self):
        self._connection = self.get_connection()
        self._channel = self._connection.channel()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._channel.is_open:
            self._channel.close()
        if self._connection.is_open:
            self._connection.close()
