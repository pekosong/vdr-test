import logging
import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="blob_created_handler")
@app.event_grid_trigger(arg_name="event")
def blob_created_handler(event: func.EventGridEvent):

    logging.info(f"Event type: {event.event_type}")

    # Validation 이벤트는 그냥 로그만 찍고 끝내라
    if event.event_type == "Microsoft.EventGrid.SubscriptionValidationEvent":
        logging.info("Validation event received")
        return

    # BlobCreated만 처리
    if event.event_type != "Microsoft.Storage.BlobCreated":
        logging.info("Ignoring non-BlobCreated event")
        return

    data = event.get_json()

    logging.info(f"Event data: {data}")

    blob_url = data.get("url")
    content_type = data.get("contentType")
    content_length = data.get("contentLength")

    logging.info(f"Blob URL: {blob_url}")
    logging.info(f"Content Type: {content_type}")
    logging.info(f"Content Length: {content_length}")
