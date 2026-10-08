import pika
import argparse
from common import get_connection

parser = argparse.ArgumentParser()
parser.add_argument(
    "--offset",
    type=str,
    default="first",
    choices=["first", "next", "last"],
    help="Stream offset",
)
args = parser.parse_args()

connection = get_connection()
channel = connection.channel()

q_name = "demo.stream"
channel.queue_declare(queue=q_name, durable=True, arguments={"x-queue-type": "stream"})

# slide 21: Stream consumers over AMQP must set basic_qos(prefetch_count=...)
channel.basic_qos(prefetch_count=10)

print(f"Consuming from stream '{q_name}' with offset='{args.offset}'...")


def callback(ch, method, properties, body):
    print(f"[x] Read stream event: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(
    queue=q_name,
    on_message_callback=callback,
    auto_ack=False,
    arguments={"x-stream-offset": args.offset},
)

try:
    print("Waiting for messages. Press Ctrl+C to stop.")
    channel.start_consuming()
except KeyboardInterrupt:
    print("\nStopped.")
    channel.stop_consuming()

connection.close()
