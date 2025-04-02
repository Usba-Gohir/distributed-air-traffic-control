import pika
import json
import threading
import time
import queue

# Simulate 3 runways
runways = ["Runway A", "Runway B", "Runway C"]
runway_status = {r: "available" for r in runways}
runway_lock = threading.Lock()

task_queue = queue.Queue()
ack_queue = queue.Queue()  # NEW: For sending ack/nack safely

def get_available_runway():
    with runway_lock:
        for runway, status in runway_status.items():
            if status == "available":
                runway_status[runway] = "busy"
                return runway
    return None

def landing_worker():
    while True:
        plane, delivery_tag = task_queue.get()
        if plane is None:
            break

        runway = get_available_runway()
        if not runway:
            print(f"⛔ All runways busy. Holding plane: {plane['plane_id']}")
            time.sleep(2)
            ack_queue.put(("nack", delivery_tag))  # Tell main thread to nack
            continue

        print(f"✅ Assigned {plane['plane_id']} ({plane['plane_type']}, {plane['priority']}) to {runway}")
        time.sleep(3)
        with runway_lock:
            runway_status[runway] = "available"
        print(f"🟢 {runway} is now available")

        ack_queue.put(("ack", delivery_tag))  # Tell main thread to ack

def callback(ch, method, properties, body):
    plane = json.loads(body)
    task_queue.put((plane, method.delivery_tag))

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="ready_for_landing")
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(queue="ready_for_landing", on_message_callback=callback)

    # Start worker threads
    for _ in range(5):
        threading.Thread(target=landing_worker, daemon=True).start()

    print("[🛬 RUNWAY MANAGER] Listening for incoming planes...")

    try:
        while True:
            connection.process_data_events(time_limit=1)

            # Process acks from worker threads
            while not ack_queue.empty():
                action, tag = ack_queue.get()
                try:
                    if action == "ack":
                        channel.basic_ack(delivery_tag=tag)
                    elif action == "nack":
                        channel.basic_nack(delivery_tag=tag, requeue=True)
                except Exception as e:
                    print(f"⚠️ Error on {action}: {e}")
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
