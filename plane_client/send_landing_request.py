# Connects to a local RabbitMQ server
# Randomly generates a new plane ID and type
# Sends a landing request as a JSON message to the "landing_queue"

import pika
import json
import uuid
import random

def send_landing_request():
    # Connect to RabbitMQ server (running on localhost)
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Declare the queue if it doesn't exist
    channel.queue_declare(queue="landing_queue")

    # Generate fake plane data
    plane_id = str(uuid.uuid4())[:8]
    plane_type = random.choice(["small", "medium", "large"])
    priority = random.choice(["normal", "vip", "emergency"])

    request = {
        "plane_id": plane_id,
        "plane_type": plane_type,
        "priority": priority
    }

    # Send the landing request as JSON
    channel.basic_publish(
        exchange="",
        routing_key="landing_queue",
        body=json.dumps(request)
    )

    print(f"[✈️ Sent] Landing Request: {request}")
    connection.close()

if __name__ == "__main__":
    send_landing_request()
