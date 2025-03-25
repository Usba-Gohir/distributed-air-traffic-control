# Assigns planes to available runways using RabbitMQ
# Supports concurrency with thread-safe runway assignment

import time
import pika
import json
import threading
import random

# Simulate 3 runways
runways = ["Runway A", "Runway B", "Runway C"]
runway_status = {r: "available" for r in runways}

# Lock to make runway access thread-safe
runway_lock = threading.Lock()

def get_available_runway():
    with runway_lock:
        for runway, status in runway_status.items():
            if status == "available":
                runway_status[runway] = "busy"  # Reserve it immediately
                return runway
    return None

def handle_landing(plane, ch, delivery_tag):
    runway = get_available_runway()
    if not runway:
        print(f"⛔ All runways busy. Holding plane: {plane['plane_id']}")
        time.sleep(2)
        ch.basic_nack(delivery_tag=delivery_tag, requeue=True)
        return

    print(f"✅ Assigned {plane['plane_id']} ({plane['plane_type']}, {plane['priority']}) to {runway}")
    time.sleep(3)  # simulate landing
    with runway_lock:
        runway_status[runway] = "available"
    print(f"🟢 {runway} is now available")

    ch.basic_ack(delivery_tag=delivery_tag)

def callback(ch, method, properties, body):
    plane = json.loads(body)
    threading.Thread(target=handle_landing, args=(plane, ch, method.delivery_tag)).start()

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="ready_for_landing")

    # Let RabbitMQ send multiple messages (concurrent consumption)
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(queue="ready_for_landing", on_message_callback=callback)

    print("[🛬 RUNWAY MANAGER] Listening for incoming planes...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
