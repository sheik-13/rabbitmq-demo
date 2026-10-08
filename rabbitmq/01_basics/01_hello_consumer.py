import pika
from common import get_connection

print("Connecting to RabbitMQ...")
connection = get_connection()
channel = connection.channel()

# slide 10: durable queue "hello"
print("Declaring durable queue 'hello'...")
channel.queue_declare(queue="hello", durable=True)


def callback(ch, method, properties, body):
    print(f"Received -> {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("Acknowledged message.")


print("Starting to consume (manual ack)...")
channel.basic_consume(queue="hello", on_message_callback=callback, auto_ack=False)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopped by user.")
    channel.stop_consuming()

connection.close()
