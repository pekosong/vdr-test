import azure.functions as func
import logging
import json

# FunctionApp 인스턴스 생성하는 부분
app = func.FunctionApp()


@app.function_name(name="BlobCreatedHandler")
@app.event_grid_trigger(arg_name="event")
def blob_created_handler(event: func.EventGridEvent):
    logging.info(f"--- Event Grid Triggered ---")
    logging.info(f"Event ID: {event.id}")
    logging.info(f"Event type: {event.event_type}")

    # 1. Validation 이벤트 처리 (구독 인증용)
    if event.event_type == "Microsoft.EventGrid.SubscriptionValidationEvent":
        logging.info("Validation event received and processed.")
        return

    # 2. BlobCreated 이벤트만 필터링
    if event.event_type != "Microsoft.Storage.BlobCreated":
        logging.info(f"Ignoring non-BlobCreated event: {event.event_type}")
        return

    # 3. 데이터 추출
    try:
        data = event.get_json()
        logging.info(f"Event data: {json.dumps(data, indent=2)}")

        blob_url = data.get("url")
        content_type = data.get("contentType")
        content_length = data.get("contentLength")

        # 결과 출력
        logging.info(f"✅ Processing complete:")
        logging.info(f"   - Blob URL: {blob_url}")
        logging.info(f"   - Content Type: {content_type}")
        logging.info(f"   - Content Length: {content_length} bytes")

    except Exception as e:
        logging.error(f"Error parsing event data: {str(e)}")
