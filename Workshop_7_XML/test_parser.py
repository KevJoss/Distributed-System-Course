import os
from lxml import etree

class XMLValidatorWrapper:
    def __init__(self, xsd_path):
        with open(xsd_path, 'rb') as f:
            self.schema = etree.XMLSchema(etree.XML(f.read()))

    def validate_and_parse(self, xml_string):
        try:
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            self.schema.assertValid(xml_doc)
            return True, xml_doc, "Valid Schema"
        except etree.DocumentInvalid as e:
            return False, None, str(e)
        except etree.XMLSyntaxError as e:
            return False, None, f"Syntax Error: {str(e)}"

def fastapi_broker_wrapper(xml_payload):
    print("\n--- [BROKER] Receiving external request ---")
    validator = XMLValidatorWrapper("schemas/ingestion.xsd")
    is_valid, doc, msg = validator.validate_and_parse(xml_payload)
    
    if not is_valid:
        print(f"[BROKER] 400 Bad Request. Validation Failed: {msg}")
        return None

    request_id = doc.findtext("RequestID")
    image_id = doc.findtext("AttachedImage/ImageID")
    original_file_name = doc.findtext("AttachedImage/OriginalFileName")
    print(f"[BROKER] 202 Accepted. Request: {request_id}. Image stored as: {original_file_name}")
    
    internal_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <DiagnosticTask>
        <TaskID>{request_id}</TaskID>
        <Payload>
            <ImageID>{image_id}</ImageID>
            <ImagePath>/shared/{original_file_name}</ImagePath>
            <DetectedCrop>Pending</DetectedCrop>
        </Payload>
        <State><CurrentStatus>Queued</CurrentStatus></State>
    </DiagnosticTask>"""
    
    print("[BROKER] Internal XML generated. Enqueueing to Redis (router_queue)...")
    print("INTERNAL XML:\n", internal_xml)
    return internal_xml

def router_worker_wrapper(internal_xml):
    print("\n--- [ROUTER WORKER] Consuming from Redis ---")
    validator = XMLValidatorWrapper("schemas/internal.xsd")
    is_valid, doc, msg = validator.validate_and_parse(internal_xml)
    
    if not is_valid:
        print(f"[ROUTER] Dropping corrupted message: {msg}")
        return

    task_id = doc.findtext("TaskID")
    image_path = doc.findtext("Payload/ImagePath")
    
    print(f"[ROUTER] Valid payload. Task: {task_id}. Image: {image_path}")
    print("[ROUTER] Simulating AI classification...")
    
    simulated_crop = "Tomato"
    
    if simulated_crop == "Background":
        print("[ROUTER] Result: Background. Updating DB to 'Invalid'. Dropping task.")
    else:
        print(f"[ROUTER] Result: {simulated_crop}. Routing to {simulated_crop.lower()}_queue.")

if __name__ == "__main__":
    valid_ui_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <UploadRequest>
        <RequestID>1</RequestID>
        <Client><Username>eolivo</Username></Client>
        <Timestamp>2026-04-08T10:00:00Z</Timestamp>
        <AttachedImage>
            <ImageID>1</ImageID>
            <OriginalFileName>leaf.jpg</OriginalFileName>
        </AttachedImage>
        <Status>Submitted</Status>
    </UploadRequest>"""

    invalid_ui_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <UploadRequest>
        <RequestID>req-002</RequestID>
        <Client><Username>eolivo</Username></Client>
        <Timestamp>2026-04-08</Timestamp> <AttachedImage>
            <ImageID>img-xyz</ImageID>
            <OriginalFileName>leaf.jpg</OriginalFileName>
        </AttachedImage>
        <Status>HackedStatus</Status> </UploadRequest>"""

    print("=== TEST CASE 1: VALID UPLOAD ===")
    internal_payload = fastapi_broker_wrapper(valid_ui_xml)
    if internal_payload:
        router_worker_wrapper(internal_payload)

    # print("\n=== TEST CASE 2: INVALID UPLOAD (SIMULATING ATTACK/BUG) ===")
    # fastapi_broker_wrapper(invalid_ui_xml)