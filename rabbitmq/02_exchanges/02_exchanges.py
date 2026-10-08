import pika
from common import get_connection

connection = get_connection()
channel = connection.channel()

print("Setting up exchanges and queues...")

# 1. Direct Exchange
channel.exchange_declare(exchange="demo.direct", exchange_type="direct", durable=True)
for q in ["demo.errors", "demo.info"]:
    channel.queue_declare(queue=q, durable=True)
channel.queue_bind(queue="demo.errors", exchange="demo.direct", routing_key="error")
channel.queue_bind(queue="demo.info", exchange="demo.direct", routing_key="info")

# 2. Fanout Exchange
channel.exchange_declare(exchange="demo.fanout", exchange_type="fanout", durable=True)
for q in ["demo.email", "demo.sms", "demo.analytics"]:
    channel.queue_declare(queue=q, durable=True)
    channel.queue_bind(queue=q, exchange="demo.fanout", routing_key="")

# 3. Topic Exchange
channel.exchange_declare(exchange="demo.topic", exchange_type="topic", durable=True)
for q in ["demo.orders.eu", "demo.orders.all"]:
    channel.queue_declare(queue=q, durable=True)
channel.queue_bind(
    queue="demo.orders.eu", exchange="demo.topic", routing_key="orders.*.eu"
)
channel.queue_bind(
    queue="demo.orders.all", exchange="demo.topic", routing_key="orders.#"
)

# 4. Headers Exchange
channel.exchange_declare(exchange="demo.headers", exchange_type="headers", durable=True)
channel.queue_declare(queue="demo.pdf", durable=True)
channel.queue_bind(
    queue="demo.pdf",
    exchange="demo.headers",
    routing_key="",
    arguments={"x-match": "all", "format": "pdf"},
)

print("Publishing examples...")

# Direct example
print("key=error -> expect: demo.errors only")
channel.basic_publish(
    exchange="demo.direct", routing_key="error", body="An error occurred!"
)

# Fanout example
print("fanout publish -> expect: demo.email, demo.sms, demo.analytics")
channel.basic_publish(exchange="demo.fanout", routing_key="", body="Broadcast message!")

# Topic example
print("key=orders.new.eu -> expect: demo.orders.eu AND demo.orders.all")
channel.basic_publish(
    exchange="demo.topic", routing_key="orders.new.eu", body="EU order"
)
print("key=orders.new.us -> expect: demo.orders.all only")
channel.basic_publish(
    exchange="demo.topic", routing_key="orders.new.us", body="US order"
)

# Headers example
print("headers format=pdf -> expect: demo.pdf only")
channel.basic_publish(
    exchange="demo.headers",
    routing_key="",
    body="PDF doc",
    properties=pika.BasicProperties(headers={"format": "pdf"}),
)
print("headers format=txt -> expect: nothing")
channel.basic_publish(
    exchange="demo.headers",
    routing_key="",
    body="TXT doc",
    properties=pika.BasicProperties(headers={"format": "txt"}),
)

print("Done. Messages are ready to be inspected in the Management UI.")
connection.close()
