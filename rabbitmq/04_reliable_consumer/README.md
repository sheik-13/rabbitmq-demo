# Part 4 — Reliable Consumer

## Idea

The consumer acknowledges only after its simulated work completes. That makes
unacknowledged work visible and lets RabbitMQ redeliver it if the worker dies.

## Crash and redelivery

```bash
docker compose up -d --wait
python 04_reliable_consumer.py --publish --prefetch 1 --sleep 10
```

While the first task says `Working`, show **Unacked = 1** in `demo.reliable`.
Press Ctrl+C. The connection closes and the task returns to **Ready**. Start a
consumer again to show the redelivery:

```bash
python 04_reliable_consumer.py --prefetch 1 --sleep 1
```

## Prefetch fairness

After resetting, start the following in two terminals a few seconds apart:

```bash
python 04_reliable_consumer.py --publish --prefetch 1 --sleep 10
python 04_reliable_consumer.py --prefetch 1 --sleep 10
```

With prefetch `1`, each worker holds one unacknowledged task at a time. Repeat
with a larger prefetch value to show one consumer reserving more work.

## Dead-letter queue

```bash
python 04_dlq_demo.py
```

The consumer rejects the poison message with `requeue=False`. Open `demo.dlq`
to show the message sent through `demo.dlx` rather than silently discarded.

Say: “An acknowledgement is a signature on delivery; without it, RabbitMQ can
give the work to someone else.”

## Reset

```bash
docker compose down -v
```
