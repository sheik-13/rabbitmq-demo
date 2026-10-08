import pika
from common import get_connection

connection = get_connection()
channel = connection.channel()

# 1. Classic Queue
print("Declaring Classic queue 'demo.classic'...")
channel.queue_declare(
    queue="demo.classic", durable=True, arguments={"x-queue-type": "classic"}
)

# 2. Quorum Queue
print("Declaring Quorum queue 'demo.quorum'...")
channel.queue_declare(
    queue="demo.quorum", durable=True, arguments={"x-queue-type": "quorum"}
)

# 3. Stream Queue
print("Declaring Stream queue 'demo.stream'...")
channel.queue_declare(
    queue="demo.stream", durable=True, arguments={"x-queue-type": "stream"}
)

# Publish to Classic & Quorum
for q in ["demo.classic", "demo.quorum"]:
    print(f"Publishing 3 messages to {q}...")
    for i in range(3):
        channel.basic_publish(exchange="", routing_key=q, body=f"Msg {i+1} for {q}")

for q in ["demo.classic", "demo.quorum"]:
    print(f"Consuming from {q} (messages will be removed)...")
    for _ in range(3):
        method_frame, header_frame, body = channel.basic_get(queue=q, auto_ack=False)
        if method_frame:
            print(f"  [x] Consumed: {body.decode()}")
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    print(f"Queue {q} is now empty.")

# Publish to Stream
print("Publishing 5 messages to demo.stream...")
for i in range(5):
    channel.basic_publish(
        exchange="", routing_key="demo.stream", body=f"Stream Event {i+1}"
    )
print("Messages stay in the stream. Run 05_stream_consumer.py to read them.")

connection.close()
