import sys
import pika
from common import get_connection

# slide 14: durable queue + persistent message
transient = "--transient" in sys.argv

connection = get_connection()
channel = connection.channel()
# Publisher confirms
channel.confirm_delivery()

if transient:
    q_name = "demo.transient"
    print(f"Declaring transient queue '{q_name}'...")
    channel.queue_declare(queue=q_name, durable=False)

    print("Publishing non-persistent message...")
    try:
        channel.basic_publish(
            exchange="",
            routing_key=q_name,
            body="I will not survive a restart",
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Transient),
            mandatory=True,
        )
        print("Message sent successfully.")
    except pika.exceptions.UnroutableError:
        print("Error: Message unroutable!")
    except pika.exceptions.NackError:
        print("Error: Message NACKed by broker!")

else:
    q_name = "demo.reliable"
    print(f"Declaring durable quorum queue '{q_name}'...")
    channel.queue_declare(
        queue=q_name, durable=True, arguments={"x-queue-type": "quorum"}
    )

    print("Publishing persistent message...")
    try:
        channel.basic_publish(
            exchange="",
            routing_key=q_name,
            body="I WILL survive a restart",
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
            mandatory=True,
        )
        print("Message sent and confirmed successfully.")
    except pika.exceptions.UnroutableError:
        print("Error: Message unroutable!")
    except pika.exceptions.NackError:
        print("Error: Message NACKed by broker!")

print("Check the UI, then run: docker restart rabbit")
connection.close()
