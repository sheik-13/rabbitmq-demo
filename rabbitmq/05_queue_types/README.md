# Part 5 — Queue Types

## Idea

Queues have different storage and delivery semantics. Their type is chosen at
declaration time and cannot be changed later.

## Run it

```bash
docker compose up -d --wait
python 05_queue_types.py
```

Open **Queues and Streams** and show the **Type** column:

- `demo.classic` is the original, single-node queue.
- `demo.quorum` is durable and uses Raft; on this one-node demo it has one
  replica.
- `demo.stream` is an append-only log.

The script publishes and consumes three classic and quorum messages, so both
queues return to zero. It publishes five stream events, which remain stored.

## Replay a stream

```bash
python 05_stream_consumer.py --offset first
```

It reads all stored events and manually acknowledges them, but the stream still
shows five messages. Stop it with Ctrl+C. Next, run:

```bash
python 05_stream_consumer.py --offset next
```

It waits for events created after it started. In another terminal, rerun
`python 05_queue_types.py` to add five new stream events; only those new events
appear in the `next` reader.

Say: “Classic and quorum queues are work inboxes. A stream is a DVR: many
readers can replay the recording without erasing it.”

## Reset

```bash
docker compose down -v
```
