import json
import os
import requests

STRIPE_SIGNING_SECRET = os.getenv("STRIPE_SIGNING_SECRET", "whsec_sample_key")

def handle_webhook(event, context):
    """Serverless entrypoint handler for webhook processing."""
    try:
        body = json.loads(event.get("body", "{}"))
        event_type = body.get("type", "unknown")
        
        print(f"Processing event: {event_type}")
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "acknowledged", "event": event_type})
        }
    except Exception as err:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(err)})
        }
