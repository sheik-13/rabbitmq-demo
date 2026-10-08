# Part 1 — Producer and Consumer

## Idea

The default exchange is the post office's front desk. Every queue is already
addressable by its own name, so a message addressed to `hello` goes to the
`hello` queue without declaring a named exchange.

## Run it

```bash
docker compose up -d --wait
python 01_hello_producer.py
```

In the Management UI, open **Queues and Streams** and show `hello` with
**Ready = 1**. Then run:

```bash
python 01_hello_consumer.py
```

The consumer keeps waiting after it acknowledges the message; press Ctrl+C
when the audience has seen `Received` and `Acknowledged`. Refresh the queue to
show **Ready = 0**.

## What to point out

- `exchange=""` means the nameless default exchange.
- `routing_key="hello"` is the postal address.
- Both scripts declare the queue, so either can be run first.
- `auto_ack=False` and `basic_ack` mean the worker, not RabbitMQ, decides when
  work is complete.

Say: “The producer leaves a letter at the post office; the queue holds it
until a worker signs for it.”

## Reset

```bash
docker compose down -v
```
