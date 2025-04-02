
# 🛫 Distributed Air Traffic Control System

This is a fully functional distributed air traffic control simulation system built with **Python**, **RabbitMQ**, and **multithreading**. It models real-time coordination between planes, an ATC service, and a runway manager that assigns planes to available runways based on **priority** and **availability**.

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [System Components](#-system-components)
- [Priority Queue Logic](#-priority-queue-logic)
- [Concurrency with Threads](#-concurrency-with-threads)
- [How to Run the System](#-how-to-run-the-system)
- [Demonstration](#-demonstration)
- [Future Improvements](#-future-improvements)

---

## 🚀 Overview

The purpose of this system is to simulate the real-time process of receiving landing requests from airplanes and managing their safe landings across multiple runways using a **priority-based queuing system**.

The project consists of:
- Planes requesting to land (clients)
- An ATC service managing requests and sorting by priority
- A runway manager assigning available runways using concurrency

---

## 🛠️ Tech Stack

| Tool/Library      | Purpose                            |
|-------------------|------------------------------------|
| Python 3.11+       | Core programming language          |
| RabbitMQ          | Asynchronous messaging              |
| `pika`            | Python RabbitMQ client              |
| `threading`       | Runway concurrency                  |
| PowerShell / Terminal | Running multiple services      |

---

## 🏗️ Architecture

```
Plane Client  →  ATC Service  →  Runway Manager
   🛩️               🗼                   🛬
 Sends plane   →  Receives request   → Assigns runways
 request         Sorts by priority     using threads
 via RabbitMQ    Forwards top plane    Simulates landing time
```

**Queues:**
- `landing_queue` – Planes send landing requests here
- `ready_for_landing` – ATC forwards sorted plane requests here

---

## 🧩 System Components

### 1. `plane_client/send_landing_request.py`
Sends a single random landing request (plane ID, type, priority) to the `landing_queue`.

### 2. `plane_client/send_multiple_planes.py`
Uses Python `threading` to send multiple landing requests **simultaneously**, mimicking real-world air traffic congestion.

### 3. `atc_service/receive_landing_requests.py`
- Listens to `landing_queue`
- Parses JSON messages
- Stores requests in a **heap-based priority queue**
- Forwards the highest-priority plane to `ready_for_landing`

### 4. `runway_manager/assign_runway.py`
- Listens to `ready_for_landing` queue
- Assigns planes to any **available runway (A, B, C)**
- If all runways are busy, plane is requeued
- Landing process is **handled using threads**, so multiple planes can land in parallel

---

## 🧠 Priority Queue Logic

Planes are prioritized using the following mapping:

| Priority     | Value |
|--------------|-------|
| `emergency`  | 0     |
| `vip`        | 1     |
| `normal`     | 2     |

The ATC uses a **heap queue (`heapq`)** to always pop the plane with the highest priority first. This simulates real-world priority handling in ATC towers.

---

## 🧵 Concurrency with Threads

The `assign_runway.py` script uses **`threading.Thread`** to:
- Handle multiple landing requests **at the same time**
- Free up runways after a delay
- Reassign held planes once runways become available

This mimics how an actual control tower might manage simultaneous landings across multiple runways.

---

## 🧪 How to Run the System

### 1. Start RabbitMQ
Make sure RabbitMQ is running via Docker:

```bash
docker start rabbitmq
```

Visit: [http://localhost:15672](http://localhost:15672)

- Username: `guest`
- Password: `guest`

---

### 2. Activate Virtual Environment

```bash
cd distributed_air_traffic_control
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install pika
```

---

### 4. Open 3 Terminal Tabs

**Tab 1: Start ATC Service**
```bash
python atc_service/receive_landing_requests.py
```

**Tab 2: Start Runway Manager**
```bash
python runway_manager/assign_runway.py
```

**Tab 3: Send Plane Requests**
```bash
# Option 1: Send 1 plane at a time
python plane_client/send_landing_request.py

# Option 2: Send multiple planes using threads
python plane_client/send_multiple_planes.py
```

---

## 📸 Demonstration (Sample Output)

```
[🛫 Sent] Landing Request: {'plane_id': 'abc123', 'priority': 'vip'}

[🗼 ATC SERVICE] Waiting for landing requests...
[🛬 RECEIVED] Plane abc123 | Priority: vip
📦 Forwarded to Runway Manager: abc123

[🛬 RUNWAY MANAGER] Listening for incoming planes...
✅ Assigned abc123 (vip) to Runway B
🟢 Runway B is now available
```

If all runways are busy:
```
⛔ All runways busy. Holding plane: def456
```

---

## 🧠 Future Improvements

- ✅ Log queue status to a file
- 🔄 Add real-time GUI to view runway usage
- ⏱️ Simulate delays based on weather or maintenance
- 🌐 Add a REST API to view live data
- 📈 Visualize queue history in a dashboard

---


---

## 📜 License

This project is for educational purposes only.
