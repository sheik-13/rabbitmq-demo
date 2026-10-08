# AGENTS.md — RabbitMQ in Production: Live Demo

Guidance for AI coding agents (and humans) working on this repository.
This repo holds the **live demo** for the tech talk **"RabbitMQ in Production"** (26-slide deck).
The demo is shown on stage, so **clarity, reliability and readability beat cleverness**.

---

## 1. Goal and audience

Show the audience, with real code and the Management UI, how these things work:

1. **Producer and consumer**: how messages are sent and received
2. **Exchanges and their types**: direct, fanout, topic, headers (plus the default exchange)
3. **Queues and their types**: classic, quorum, stream
4. **Producer reliability**: durability, persistent messages, publisher confirms
5. **Consumer reliability**: manual acks, redelivery, prefetch, dead-letter queues
6. **Monitoring**: watching queue depth grow and drain (optional cluster failover)

The audience may have **no prior knowledge** of message brokers. Keep the post office analogy from the slides.
Total target runtime: **about 25-30 minutes** of demo, spread across the talk (see section 4).

---

## 2. Tech stack

| Item | Choice |
|---|---|
| Broker | `rabbitmq:4-management` (Docker) |
| Language | Python 3.10+ |
| Client library | `pika` (>= 1.3, uses `pika.DeliveryMode`) |
| Protocol | AMQP 0-9-1 |
| UI | Management UI at http://localhost:15672 (`guest` / `guest`, demo only) |
| Ports | 5672 (AMQP), 15672 (UI), 15692 (Prometheus metrics) |

Do not add other languages, frameworks or heavy dependencies. The audience must be able to read every script on a projector.

---

## 3. Repository layout

Scripts are numbered **in the order they are shown on stage**. Keep that numbering.

```
.
├── AGENTS.md
├── README.md                     # one-page cheat sheet with exact commands
├── demo_gui.py                   # tkinter GUI to run demos
├── 01_basics/
│   ├── docker-compose.yml
│   ├── common.py
│   └── ...
├── 02_exchanges/
├── 03_reliable_producer/
├── 04_reliable_consumer/
├── 05_queue_types/
├── 06_monitoring/            # 3 modes: clean / preloaded / cluster (heavily commented)
├── config/
│   ├── rabbitmq.conf             # clean single node
│   ├── rabbitmq-preloaded.conf   # loads definitions.json
│   ├── rabbitmq-cluster.conf     # 3-node classic_config peer discovery
│   └── definitions.json          # every exchange type + queue type pre-created
├── requirements.txt              # pika only
├── common.py                     # shared connection helper + constants (keep tiny)
├── 01_hello_producer.py          # Part 1: default exchange, queue "hello"
├── 01_hello_consumer.py
├── 02_exchanges.py               # Part 2: direct, fanout, topic, headers
├── 03_reliable_producer.py       # Part 3: confirms + persistent messages
├── 04_reliable_consumer.py       # Part 4: manual ack, slow worker, prefetch
├── 04_dlq_demo.py                # Part 4 (optional): reject -> dead-letter queue
├── 05_queue_types.py             # Part 5: declare classic, quorum, stream queues
├── 05_stream_consumer.py         # Part 5: replay a stream from the start
├── 06_monitoring_load.py         # Part 6: fast producer with no consumer
├── cleanup.py                    # delete every demo.* exchange/queue (and "hello")
└── scripts/
    ├── start.sh                  # docker compose up -d + wait until healthy
    └── reset.sh                  # cleanup.py + restart to a known state
```

---

## 4. Demo run sheet (stage order, tied to slides)

| Part | When (after slide) | Topic | Time | Scripts | What the audience sees in the UI |
|---|---|---|---|---|---|
| 0 | 5 | **UI tour** | 2 min | none | Overview, Connections, Channels, Exchanges, Queues tabs; built-in exchanges incl. `(AMQP default)` |
| 1 | 5 / 10 / 12 | **Producer and consumer basics** | 4 min | `01_*` | `hello` queue: Ready 1 -> 0; one Connection with Channels inside |
| 2 | 10 | **Exchange types** | 8 min | `02_exchanges.py` | Bindings diagram per exchange; **Get messages** per queue |
| 3 | 15 | **Producer reliability** | 3 min | `03_reliable_producer.py` | Persistent message survives `docker restart rabbit`; transient one vanishes |
| 4 | 16-17 | **Consumer reliability** | 4 min | `04_*` | Unacked vs Ready; redelivery after Ctrl+C; prefetch fairness; DLQ |
| 5 | 21 | **Queue types** | 5 min | `05_*` | Type column in Queues tab; stream messages stay after reading |
| (opt) | 22 | **Cluster failover** | 2 min | cluster profile | Leader election after `docker stop rabbit1` (**pre-record a video**) |
| 6 | 23 | **Monitoring** | 3 min | `06_monitoring_load.py` | Queue depth climbs with no consumer, drains once a consumer starts; metrics on :15692 |

Note: the order above follows the slide order, not the order the topics were first planned.

### Part 0: UI tour
Open each tab and say: "These are the four building blocks, and this is where we will see them." Point out the default exchange (sets up slide 10).

### Part 1: Producer and consumer (`01_*`)
- Producer: connect, declare durable queue `hello`, publish one message via the default exchange (`exchange=""`, `routing_key="hello"`), print `sent`, close.
- Consumer: declare the same queue, consume with **manual ack**, print each message.
- Each file under about 20 lines. Print what is happening so the audience can follow without the UI.
- Flow: run producer (UI: Ready = 1) -> run consumer (message prints, queue back to 0) -> show **Connections** and **Channels** tabs (slide 12: one connection, many channels).

### Part 2: Exchange types (`02_exchanges.py`)
Declare exchanges, queues and bindings, then publish one example message per type:
- **Direct** (`demo.direct`): keys `error` and `info`. Publish key `error` -> only `demo.errors` receives it.
- **Fanout** (`demo.fanout`): three queues (`demo.email`, `demo.sms`, `demo.analytics`). One publish -> a copy in all three.
- **Topic** (`demo.topic`): bindings `orders.*.eu` and `orders.#`. Publish `orders.new.eu` (matches both) and `orders.new.us` (matches only `orders.#`).
- **Headers** (`demo.headers`): binding `format=pdf`, `x-match=all`. Publish one matching and one non-matching message.
- **Default exchange**: already shown in Part 1; mention it again here.
- Print a line per publish stating **what should happen**, e.g. `key=error -> expect: demo.errors only`.
- Messages must stay in the queues so they can be inspected with **Get messages** in the UI. Do not consume them in this script.

### Part 3: Producer reliability (`03_reliable_producer.py`)
- Call `channel.confirm_delivery()`.
- Publish with `properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)` to a durable queue (`demo.reliable`).
- Catch `pika.exceptions.UnroutableError` and `NackError` and print a clear message (use `mandatory=True` to show an unroutable publish being reported).
- Include a `--transient` flag that publishes a non-persistent message to a non-durable queue (`demo.transient`).
- **Restart test:** publish both, run `docker restart rabbit`, show the durable/persistent message is still there and the transient one is gone. Say: "durability = queue + message" (slide 14).

### Part 4: Consumer reliability (`04_*`)
- Consumer simulates slow work (`time.sleep`, default 10 s, configurable) **before** acking, so the message visibly sits as **Unacked**.
- **Crash test:** Ctrl+C mid-processing -> message returns to **Ready** and is redelivered to the next consumer (slide 16).
- `--prefetch N`: publish 10 messages, start two consumers with `prefetch_count=1` to show fair sharing, then a large value to show one consumer hoarding unacked messages.
- **DLQ (optional, `04_dlq_demo.py`):** use `demo.work` (dead-letters into `demo.dlx`, routing key `dead`, target queue `demo.dlq`). Reject with `basic_reject(delivery_tag, requeue=False)` and show it arriving in the DLQ (slide 17). Mention that backoff is built in the app, and quorum queues also have a delivery limit.

### Part 5: Queue types (`05_*`)
- Declare three queues with `arguments={"x-queue-type": "classic" | "quorum" | "stream"}`; all `durable=True`.
- Open the **Queues** tab and show the **Type** column and each type's features.
- Classic and quorum: publish 3 messages, consume them, they are removed.
- **Stream:** publish 5 messages, consume with two consumers using `x-stream-offset` = `first` (replay everything) and `next` (only new messages). The messages are still there after reading (DVR analogy, slide 21).
- Stream consumers over AMQP must set `basic_qos(prefetch_count=...)` and use **manual ack**.
- Quorum and stream queues cannot be exclusive or auto-delete.
- On a single node, a quorum queue has only **one replica**. Do not claim replication unless the cluster profile is used (slide 20).

### Optional: cluster failover (cluster profile)
- `docker compose --profile cluster up -d`; create a quorum queue; check the leader and followers in the UI.
- Run a producer, then `docker stop rabbit1`; show a new leader elected and messages still flowing (3 nodes survive 1 failure).
- **High risk on stage: pre-record this as a 60-second video** and play the video instead. Keep the live version only as a bonus.

### Part 6: Monitoring (`06_monitoring_load.py`)
- A fast producer publishes continuously to `demo.reliable` (or a dedicated queue) with **no consumer running**.
- Show queue depth climbing in the Overview/Queues graphs, then start a consumer and watch it drain.
- Mention metrics at http://localhost:15692/metrics and the alerts from slide 23: no consumers, growing depth, DLQ > 0, memory/disk alarms.
- The script must accept a rate and a total count, and stop by itself.

---

## 5. Docker Compose and configuration

`docker-compose.yml` runs the broker in **three modes** (use ONE at a time; they share ports 5672 / 15672):

| Mode | Command | Use |
|---|---|---|
| **Clean** (default) | `docker compose up -d` | Empty broker; scripts create everything live |
| **Pre-loaded** | `docker compose --profile preloaded up -d rabbit-preloaded` | All exchange and queue types already exist (UI walkthrough, or backup if the live demo breaks) |
| **Cluster** | `docker compose --profile cluster up -d` | 3 nodes (UI ports 15672 / 15673 / 15674) for quorum replication and failover |

- Reset: `docker compose down -v` (`-v` also deletes stored messages).
- Broker data is in Docker volumes, so `docker restart rabbit` keeps durable messages (needed for the Part 3 restart test).
- Config uses `loopback_users.guest = false` so the `guest` login works from the host. **Demo only.**
- The compose file's header comments explain every exchange type and queue type (keep them accurate and in sync with the slides; do not shorten them).
- Docker is not guaranteed to be available where an agent runs. If an agent cannot run Docker, it must say so and limit itself to validating YAML/JSON syntax and `python -m py_compile`.

### Pre-loaded map (`config/definitions.json`)

```
demo.direct  (direct)  --error-->  demo.errors
                       --info--->  demo.info
demo.fanout  (fanout)  --(all)-->  demo.email, demo.sms, demo.analytics
demo.topic   (topic)   --orders.*.eu-->  demo.orders.eu
                       --orders.#----->  demo.orders.all
demo.headers (headers) --format=pdf (x-match=all)--> demo.pdf
demo.dlx     (direct)  --dead-->  demo.dlq        (dead-letter target)

Queue types:  demo.classic (classic)  demo.quorum (quorum)  demo.stream (stream)
Reliability:  demo.reliable (quorum, durable)
              demo.work (classic, dead-letters into demo.dlx -> demo.dlq)
```

**Important:** if a script declares an object that already exists (pre-loaded mode), it must use **identical arguments**, otherwise RabbitMQ answers `PRECONDITION_FAILED`. Keep script declarations and `definitions.json` in sync. Objects used only by scripts (for example `demo.transient`) are not in `definitions.json`.

---

## 6. Concept cheat sheet (keep wording consistent with slides)

**Exchange types (slides 6-10)**
- **Direct**: exact match, routing key == binding key. Analogy: a letter to "123 Main St".
- **Fanout**: broadcast to every bound queue, ignores the routing key. Analogy: a radio station.
- **Topic**: dot-separated keys; `*` = exactly one word, `#` = zero or more words.
- **Headers**: matches message header attributes, `x-match=all` or `any`.
- **Default exchange**: nameless direct exchange; every queue is auto-bound under its own name.
- **Dead-letter exchange**: receives rejected, expired or over-limit messages for investigation.

**Queue types (slides 19-21)**
- **Classic**: original, single node, not replicated; mirroring removed in 4.0. Needs durable queue AND persistent messages to survive restarts.
- **Quorum**: recommended; replicated with Raft (leader + followers, majority confirms); 3 nodes survive 1 failure, 5 survive 2; always writes to disk.
- **Stream**: append-only log, reading does not delete, replay from any offset, many independent readers, kept until size/age retention.
- Queue type is set at declaration (`x-queue-type`) and **cannot be changed later**.

---

## 7. Naming conventions

All demo objects use the **`demo.`** prefix so `cleanup.py` can remove them safely and the UI stays easy to read.

| Kind | Names |
|---|---|
| Exchanges | `demo.direct`, `demo.fanout`, `demo.topic`, `demo.headers`, `demo.dlx` |
| Routing queues | `demo.errors`, `demo.info`, `demo.email`, `demo.sms`, `demo.analytics`, `demo.orders.eu`, `demo.orders.all`, `demo.pdf` |
| Queue-type queues | `demo.classic`, `demo.quorum`, `demo.stream` |
| Reliability queues | `demo.reliable`, `demo.transient`, `demo.work`, `demo.dlq` |

Exception: Part 1 uses the plain queue name `hello` on the default exchange to match slide 10. Never touch objects that do not start with `demo.` or equal `hello`.

---

## 8. Setup and commands

```bash
# start the broker (clean mode)
docker compose up -d
#   or without compose:
docker run -d --name rabbit -p 5672:5672 -p 15672:15672 -p 15692:15692 rabbitmq:4-management

# python env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# run a script
python 01_hello_producer.py

# reset between rehearsals
python cleanup.py
```

Before changing anything, confirm the broker is up: `docker ps` and open http://localhost:15672.

---

## 9. Code style rules

- **Readable on a projector:** short files, obvious names, no abstractions that hide the RabbitMQ calls. Show `exchange_declare`, `queue_declare`, `queue_bind`, `basic_publish`, `basic_consume` and `basic_ack` directly in each script.
- `BlockingConnection` only. No asyncio, no threads, no classes unless unavoidable.
- One connection per script, channels created from it (slide 12).
- Always **manual ack**; never `auto_ack=True` (except in a clearly labelled "what not to do" example).
- Declarations must be **idempotent**: re-running must not fail.
- Comments explain *why* in plain words and reference the slide, e.g. `# slide 14: durable queue + persistent message`.
- Print friendly progress messages. No logging frameworks.
- Host and credentials come from `common.py` (defaults `localhost`, `guest`/`guest`), overridable via `RABBIT_HOST`, `RABBIT_USER`, `RABBIT_PASS`.
- Format with `black` defaults; lines under 88 characters so code stays large on screen.
- Max about 40 lines per script unless noted.

---

## 10. Safety rules for agents

- The `guest` user is **for local demo only**. Never put real credentials in the repo. The talk says to delete `guest` in production; the README must repeat that.
- Never run destructive commands against anything except the local Docker containers named `rabbit`, `rabbit1`, `rabbit2`, `rabbit3`.
- `cleanup.py` may only delete exchanges and queues with the `demo.` prefix (plus `hello`). It must never remove users, vhosts or policies.
- Do not change published ports, image tags, container names or the naming conventions without updating the README and this file.
- No internet calls in scripts; venue Wi-Fi may be down. Pull the Docker image and install dependencies **before** the talk.

---

## 11. Stage and rehearsal tips (build these into the README)

- Zoom the browser to about 150% and use a large terminal font.
- Keep every command in a text file or README so it can be pasted rather than typed.
- Record a **backup video** of each part in case something breaks live (especially the restart test, the Ctrl+C crash test and the cluster failover).
- Put the demo steps into the slide **speaker notes** so the presenter does not lose their place.
- Show only one new idea at a time. Rehearse Ctrl+C and `docker restart rabbit`, which are the likeliest to go wrong.
- Keep the **pre-loaded** mode ready as a fallback: if a live script fails, switch and walk through the existing objects in the UI.

---

## 12. How to test changes

Run through the full demo in order after any change:

1. `python cleanup.py` (UI shows no `demo.*` objects)
2. Parts 1 to 6 in sequence, checking the UI after each:
   - Part 1: `hello` shows Ready 1, then 0 after the consumer runs.
   - Part 2: queue counts match the "expect" lines printed by the script.
   - Part 3: persistent message survives `docker restart rabbit`; transient message does not.
   - Part 4: Ctrl+C on the slow consumer returns the message to Ready; prefetch behaviour matches the flag; rejected message lands in `demo.dlq`.
   - Part 5: stream messages are still present after consuming; classic and quorum are empty.
   - Part 6: depth rises with no consumer and drains when one starts.
3. Repeat the Part 2 and Part 5 checks in **pre-loaded** mode to confirm no `PRECONDITION_FAILED`.
4. `python -m py_compile *.py` and `black --check .`

A change is not done until the full run-through passes **twice in a row** from a clean state.

---

## 13. Definition of done for a new or changed script

- [ ] Runs from a clean broker with no manual setup
- [ ] Re-runnable without errors (also against pre-loaded mode)
- [ ] Uses the `demo.` prefix
- [ ] Prints a clear line for every important step
- [ ] Has a comment pointing to the matching slide
- [ ] Fits on one projector screen without scrolling
- [ ] README cheat sheet updated with the exact command to run it

---

## 14. Out of scope (unless the human asks)

- A full Prometheus and Grafana setup (only mention metrics on port 15692)
- Web frameworks, databases, Kafka or SQS comparisons in code
- Performance benchmarking
