import azure.functions as func
import logging
import json
import os
from azure.storage.queue import QueueServiceClient

app = func.FunctionApp()

# 환경 변수 로드 (Azure Portal의 App Settings에서 설정해야 함)
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if CONNECTION_STRING:
    CONNECTION_STRING = CONNECTION_STRING.strip()

VM_QUEUE_NAME = os.getenv("AZURE_STORAGE_VM_QUEUE_NAME", "vdrqueue").strip()
FUNC_QUEUE_NAME = os.getenv("AZURE_STORAGE_FUNCTION_QUEUE_NAME", "vdrfuncqueue").strip()

@app.function_name(name="BlobCreatedHandler")
@app.event_grid_trigger(arg_name="event")
def blob_created_handler(event: func.EventGridEvent):
    logging.info(f"--- Event Grid Triggered ---")
    logging.info(f"Subject: {event.subject}")
    logging.info(f"Event Type: {event.event_type}")

    # Microsoft.Storage.BlobCreated 이벤트인지 확인
    if event.event_type != "Microsoft.Storage.BlobCreated":
        logging.info(f"Ignoring event type: {event.event_type}")
        return

    try:
        # 이벤트 데이터 추출
        event_data = event.get_json()
        
        # Blob URL 추출 (이벤트 스키마에 따라 다를 수 있음)
        blob_url = event_data.get("url")
        if not blob_url:
            logging.error("Blob URL not found in event data.")
            return

        logging.info(f"Processing blob: {blob_url}")

        # 파일 확장자에 따른 분기 처리
        blob_url_lower = blob_url.lower()
        target_queue = None
        office_extensions = (".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".hwp")
        
        if blob_url_lower.endswith(".pdf"):
            target_queue = FUNC_QUEUE_NAME
            logging.info(f"Routing PDF to: {target_queue}")
        elif blob_url_lower.endswith(office_extensions):
            target_queue = VM_QUEUE_NAME
            logging.info(f"Routing Office/HWP to: {target_queue}")
        else:
            logging.info(f"Unsupported file type: {blob_url}")
            return

        # 설정 확인
        if not CONNECTION_STRING:
            logging.error("AZURE_STORAGE_CONNECTION_STRING is missing in App Settings.")
            return

        if not target_queue:
            logging.error("Target queue name is not configured.")
            return

        # 큐로 메시지 전송
        queue_service_client = QueueServiceClient.from_connection_string(CONNECTION_STRING)
        queue_client = queue_service_client.get_queue_client(target_queue)
        
        message_body = {
            "url": blob_url,
            "contentType": event_data.get("contentType"),
            "contentLength": event_data.get("contentLength"),
            "timestamp": event.event_time.isoformat() if event.event_time else None,
            "subject": event.subject
        }
        
        queue_client.send_message(json.dumps(message_body))
        logging.info(f"Successfully sent message to {target_queue}")

    except Exception as e:
        logging.error(f"Error in blob_created_handler: {str(e)}", exc_info=True)
