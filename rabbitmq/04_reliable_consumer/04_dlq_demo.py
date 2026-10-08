import pika
from common import get_connection

connection = get_connection()
channel = connection.channel()

# Set up DLX and DLQ
print("Declaring DLX 'demo.dlx' and DLQ 'demo.dlq'...")
channel.exchange_declare(exchange="demo.dlx", exchange_type="direct", durable=True)
channel.queue_declare(queue="demo.dlq", durable=True)
channel.queue_bind(queue="demo.dlq", exchange="demo.dlx", routing_key="dead")

# Set up main work queue that dead-letters to DLX
print("Declaring work queue 'demo.work' with DLX config...")
channel.queue_declare(
    queue="demo.work",
    durable=True,
    arguments={
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "demo.dlx",
        "x-dead-letter-routing-key": "dead",
    },
)

# Publish a poison pill
print("Publishing a poison pill message to 'demo.work'...")
channel.basic_publish(
    exchange="",
    routing_key="demo.work",
    body="Bad format data",
    properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
)

print("Consuming from 'demo.work'...")


def callback(ch, method, properties, body):
    msg = body.decode()
    print(f"[x] Received: {msg}")
    print(
        "[!] Simulating processing failure. Rejecting without requeue (requeue=False)..."
    )
    # slide 17: DLQ Demo
    # Reject message, sending it to DLX
    ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
    print("Message rejected. Check 'demo.dlq' in the UI to see it.")
    ch.stop_consuming()


channel.basic_consume(queue="demo.work", on_message_callback=callback, auto_ack=False)
channel.start_consuming()

connection.close()
