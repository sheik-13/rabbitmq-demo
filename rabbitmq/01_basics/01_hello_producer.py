import pika
from common import get_connection

print("Connecting to RabbitMQ...")
connection = get_connection()
channel = connection.channel()

# slide 10: default exchange + durable queue "hello"
print("Declaring durable queue 'hello'...")
channel.queue_declare(queue="hello", durable=True)

print("Publishing message to the default exchange...")
channel.basic_publish(
    exchange="", routing_key="hello", body="Hello!"  # default exchange
)
print("sent -> 'Hello!'")

channel.close()
connection.close()
print("Closed connection.")
