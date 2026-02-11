import logging
import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="blob_created_handler")
@app.event_grid_trigger(arg_name="event")
def blob_created_handler(event: func.EventGridEvent):

    logging.info("Event received")

    # 🔥 validation 이벤트 처리
    if event.event_type == "Microsoft.EventGrid.SubscriptionValidationEvent":
        validation_data = event.get_json()
        validation_code = validation_data["validationCode"]

        logging.info("Validation event received")

        return {
            "validationResponse": validation_code
        }

    # 🔥 실제 BlobCreated 처리
    if event.event_type == "Microsoft.Storage.BlobCreated":

        data = event.get_json()

        blob_url = data.get("url")
        content_type = data.get("contentType")
        content_length = data.get("contentLength")

        logging.info(f"Blob URL: {blob_url}")
        logging.info(f"Content Type: {content_type}")
        logging.info(f"Content Length: {content_length}")
