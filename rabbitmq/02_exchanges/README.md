# Part 2 — Exchange Types

## Idea

An exchange is the post office sorting desk. Producers send to an exchange;
bindings decide which queue receives each copy. This script only publishes, so
the messages remain available for **Get messages** in the UI.

## Run it

```bash
docker compose up -d --wait
python 02_exchanges.py
```

Open **Exchanges**, select each `demo.*` exchange, and show its bindings. Then
open the destination queues and use **Get messages** (with manual
acknowledgement) to inspect the bodies.

## Expected queue counts

| Queue | Ready messages | Why |
| --- | ---: | --- |
| `demo.errors` | 1 | Direct key `error` exactly matches. |
| `demo.info` | 0 | No `info` message was published. |
| `demo.email`, `demo.sms`, `demo.analytics` | 1 each | Fanout broadcasts one copy to every binding. |
| `demo.orders.eu` | 1 | `orders.*.eu` matches `orders.new.eu`. |
| `demo.orders.all` | 2 | `orders.#` matches both order keys. |
| `demo.pdf` | 1 | Only the `format=pdf` header matches. |

Say: “A direct exchange reads an address, fanout is a radio broadcast, topic
uses address patterns, and headers inspect the envelope.”

## Reset

```bash
docker compose down -v
```
