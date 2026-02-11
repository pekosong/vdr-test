import logging
import json
import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="blob_created_handler")
@app.event_grid_trigger(arg_name="event")
def blob_created_handler(event: func.EventGridEvent):

    logging.info("Event received")

    event_type = event.event_type
    subject = event.subject
    data = event.get_json()

    logging.info(f"Event Type: {event_type}")
    logging.info(f"Subject: {subject}")
    logging.info(f"Data: {data}")

    # Blob URL 추출
    blob_url = data.get("url")
    content_type = data.get("contentType")
    content_length = data.get("contentLength")

    logging.info(f"Blob URL: {blob_url}")
    logging.info(f"Content Type: {content_type}")
    logging.info(f"Content Length: {content_length}")
