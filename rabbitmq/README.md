# RabbitMQ in Production: Live Demo

Five small, independent demos for the talk. Each folder has its own broker
definition and presenter guide, so the code stays readable on a projector.

> [!WARNING]
> `guest` / `guest` and `loopback_users.guest = false` are for this local demo
> only. Do not use them in production.

## Before the talk

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Use Docker Compose v2 (`docker compose`). Pull the image and install Python
dependencies before arriving at the venue. Each demo uses the same ports and
the container name `rabbit`, so run **one demo broker at a time**.

```bash
cd 01_basics
docker compose up -d --wait
```

Open the Management UI at http://localhost:15672 with `guest` / `guest`.
When a part is finished, remove its demo broker and messages with:

```bash
docker compose down -v
```

From the repository root, the equivalent helpers are
`./scripts/start.sh 01_basics` and `./scripts/reset.sh 01_basics`.

## Demo order

| Part | Topic | Presenter guide |
| --- | --- | --- |
| 1 | Default exchange: send and receive | [01_basics](01_basics/README.md) |
| 2 | Direct, fanout, topic, and headers exchanges | [02_exchanges](02_exchanges/README.md) |
| 3 | Durable queues, persistent messages, confirms | [03_reliable_producer](03_reliable_producer/README.md) |
| 4 | Manual acknowledgements, prefetch, DLQ | [04_reliable_consumer](04_reliable_consumer/README.md) |
| 5 | Classic, quorum, and stream queues | [05_queue_types](05_queue_types/README.md) |

Every guide includes exact commands, what to show in the UI, and a short
speaker line. Keep the browser at roughly 150% zoom and use a large terminal
font. Record a backup video for the restart and Ctrl+C moments.

## Optional GUI launcher

`python demo_gui.py` can start a selected demo and show script output. For a
live talk, the terminal commands in each guide are preferable: they make every
RabbitMQ action visible to the audience.
