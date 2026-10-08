import sys
import time
import argparse
import pika
from common import get_connection

parser = argparse.ArgumentParser()
parser.add_argument("--prefetch", type=int, default=1, help="Prefetch count")
parser.add_argument(
    "--sleep", type=int, default=10, help="Seconds to sleep per message"
)
parser.add_argument(
    "--publish", action="store_true", help="Publish 10 messages before consuming"
)
args = parser.parse_args()

connection = get_connection()
channel = connection.channel()

q_name = "demo.reliable"
channel.queue_declare(queue=q_name, durable=True, arguments={"x-queue-type": "quorum"})

if args.publish:
    print(f"Publishing 10 messages to {q_name}...")
    for i in range(10):
        channel.basic_publish(
            exchange="",
            routing_key=q_name,
            body=f"Task {i+1}",
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )
    print("Done publishing.")

print(f"Setting prefetch count to {args.prefetch}...")
channel.basic_qos(prefetch_count=args.prefetch)


def callback(ch, method, properties, body):
    msg = body.decode()
    print(f"[x] Received {msg}")
    print(
        f"    Working for {args.sleep} seconds... (Check 'Unacked' in UI or press Ctrl+C to crash)"
    )
    time.sleep(args.sleep)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"[x] Done and ACKed: {msg}")


print("Starting to consume (manual ack)...")
channel.basic_consume(queue=q_name, on_message_callback=callback, auto_ack=False)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    # slide 16: crash test mid-processing
    print("\nCrash simulated! (Message should return to Ready)")
    channel.stop_consuming()

connection.close()
