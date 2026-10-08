# Part 3 — Reliable Producer

## Idea

This is the restart test: a message survives only when both the queue is
durable and the message is persistent. Publisher confirms tell the producer
that the broker accepted the publish.

## Run it

```bash
docker compose up -d --wait
python 03_reliable_producer.py
python 03_reliable_producer.py --transient
```

In the UI, show one message in `demo.reliable` and one in `demo.transient`.
Then restart the broker without removing its volume:

```bash
docker restart rabbit
```

Refresh the UI. `demo.reliable` still has its message; `demo.transient` is
gone. The demo configuration explicitly permits RabbitMQ 4's deprecated
non-durable, non-exclusive queue shape solely so this contrast can be shown.

## What to point out

- `confirm_delivery()` turns on publisher confirms.
- `mandatory=True` makes an unroutable publish visible to the producer.
- `pika.DeliveryMode.Persistent` is the durable message.
- `pika.DeliveryMode.Transient` is deliberately discarded after restart.

Say: “Durability is a promise made twice: by the queue and by the message.”

## Reset

```bash
docker compose down -v
```
