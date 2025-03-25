# Listens to landing_queue
# Parses the JSON from each message
# Assigns priority and stores it using a heap-based priority queue
# Prints out a real-time queue of planes waiting to land

import pika
import json
import heapq

# Internal priority queue: lower number = higher priority
priority_map = {
    "emergency": 0,
    "vip": 1,
    "normal": 2
}

landing_queue = []

def callback(ch, method, properties, body):
    request = json.loads(body)
    priority = priority_map.get(request["priority"], 2)
    heapq.heappush(landing_queue, (priority, request))

    print(f"[🛬 RECEIVED] Plane {request['plane_id']} | Type: {request['plane_type']} | Priority: {request['priority']}")
    print("📋 Queue Status:", [entry[1]['plane_id'] for entry in landing_queue])

    # After adding to internal queue, forward highest priority plane to Runway Manager
    if landing_queue:
        # Remove the highest-priority plane from heap
        _, next_plane = heapq.heappop(landing_queue)

        # Send to new RabbitMQ queue for Runway Manager
        ch.basic_publish(
            exchange="",
            routing_key="ready_for_landing",
            body=json.dumps(next_plane)
        )
        print(f"📦 Forwarded to Runway Manager: {next_plane['plane_id']}")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="landing_queue")

    channel.basic_consume(
        queue="landing_queue",
        on_message_callback=callback,
        auto_ack=True
    )

    channel.queue_declare(queue="ready_for_landing")

    print("[🗼 ATC SERVICE] Waiting for landing requests...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
