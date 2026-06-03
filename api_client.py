import cv2
import requests

from config import OCR_API, PARKING_API


def process_ocr(crop_image):

    _, img_encoded = cv2.imencode(".jpg", crop_image)

    files = {
        "file": ("plate.jpg", img_encoded.tobytes(), "image/jpeg")
    }

    try:

        response = requests.post(
            OCR_API,
            files=files,
            timeout=10
        )

        print("OCR STATUS:", response.status_code)

        data = response.json()

        print("OCR RESPONSE:", data)

        if data.get("status") == "success":
            return data.get("plate_text")

        return None

    except Exception as e:

        print("OCR ERROR:", e)

        return None


def record_event(license_plate, crop_image):

    _, img_encoded = cv2.imencode(".jpg", crop_image)

    files = {
        "image": ("plate.jpg", img_encoded.tobytes(), "image/jpeg")
    }

    data = {
        "license_plate": license_plate
    }

    try:

        response = requests.post(
            PARKING_API,
            data=data,
            files=files,
            timeout=10
        )

        print("EVENT STATUS:", response.status_code)
        print("EVENT RESPONSE:", response.text)

        return response.json()

    except Exception as e:

        print("EVENT ERROR:", e)

        return None
