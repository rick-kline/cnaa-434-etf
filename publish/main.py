import base64
import json
import os
import logging

from google.cloud import pubsub_v1

# Instantiates a Pub/Sub client
publisher = pubsub_v1.PublisherClient()

# Publishes a message to a Cloud Pub/Sub topic.
def publish(request):
    request_json = request.get_json(silent=True)

    topic_name = request_json.get("topic")
    message = request_json.get("message")
    project = request_json.get("project")
    region = request_json.get("region")
    PROJECT_ID = project

    if not topic_name or not message:
        return ('Missing "topic" and/or "message" parameter.', 400)

    print(f'Publishing message to topic {topic_name}')

    # References an existing topic
    topic_path = publisher.topic_path(PROJECT_ID, topic_name)

    message_json = json.dumps({
        'data': {'message': message, 'project': project, 'region': region},
    })
    message_bytes = message_json.encode('utf-8')

    # Publishes a message
    try:
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()  # Verify the publish succeeded
        return 'Message published.'
    except Exception as e:
        print(e)
        return (e, 500)