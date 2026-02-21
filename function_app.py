import azure.functions as func
import logging
import json
import os
from azure.storage.queue import QueueServiceClient

# FunctionApp 인스턴스 생성
app = func.FunctionApp()

# 환경 변수 로드
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "DefaultEndpointsProtocol=https;AccountName=vdrtestpwc;AccountKey=G9DpkeeqYHlc4XR7Dr6A7SvAEjFpmFXFIjm4dZ6O90C4QEboZax0aE0hom/kARWMUcXdxudqWY1N+AStooAfew==;EndpointSuffix=core.windows.net")
VM_QUEUE_NAME = os.getenv("AZURE_STORAGE_VM_QUEUE_NAME", "vdrqueue")
FUNC_QUEUE_NAME = os.getenv("AZURE_STORAGE_FUNCTION_QUEUE_NAME", "vdrfuncqueue")

@app.function_name(name="BlobCreatedHandler")
@app.event_grid_trigger(arg_name="event")
def blob_created_handler(event: func.EventGridEvent):
    logging.info(f"--- Event Grid Triggered ---")
    logging.info(f"Event subject: {event.subject}")

    # BlobCreated 이벤트만 필터링합니다.
    if event.event_type != "Microsoft.Storage.BlobCreated":
        logging.info(f"Ignoring non-BlobCreated event: {event.event_type}")
        return

    # 데이터 추출 및 처리
    try:
        data = event.get_json()
        blob_url = data.get("url")
        if not blob_url:
            logging.error("Blob URL not found in event data.")
            return

        logging.info(f"Processing blob: {blob_url}")

        # 파일 확장자에 따른 분기 처리
        blob_url_lower = blob_url.lower()
        target_queue = None

        if blob_url_lower.endswith(".pdf"):
            target_queue = FUNC_QUEUE_NAME
            logging.info(f"Detected PDF file. Routing to Function Queue: {target_queue}")
        elif blob_url_lower.endswith((".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".hwp")):
            target_queue = VM_QUEUE_NAME
            logging.info(f"Detected Office/HWP file. Routing to VM Queue: {target_queue}")
        else:
            logging.info(f"Unsupported file type for queue processing: {blob_url}")
            return

        # 큐로 메시지 전송
        if CONNECTION_STRING and target_queue:
            queue_service_client = QueueServiceClient.from_connection_string(CONNECTION_STRING)
            queue_client = queue_service_client.get_queue_client(target_queue)
            
            # 메시지 내용 구성
            message_body = {
                "url": blob_url,
                "contentType": data.get("contentType"),
                "contentLength": data.get("contentLength"),
                "timestamp": event.event_time.isoformat() if event.event_time else None
            }
            
            queue_client.send_message(json.dumps(message_body))
            logging.info(f"✅ Successfully dispatched message to {target_queue}")
        else:
            logging.error("Configuration missing: CONNECTION_STRING or target_queue name is not set.")

    except Exception as e:
        logging.error(f"Error processing event: {str(e)}")
