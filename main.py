import cv2
import time
import threading

from detector import PlateDetector

from api_client import (
    process_ocr,
    record_event
)

from servo_control import open_gate

from config import COOLDOWN_SECONDS

# =====================================================
# INIT
# =====================================================

detector = PlateDetector()

cap = cv2.VideoCapture(1)

# IMPORTANT FOR PERFORMANCE
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# =====================================================
# GLOBAL STATE
# =====================================================

latest_plate = "-"

gate_status = "READY"

processing = False

last_detection_time = 0

frame_count = 0

# =====================================================
# PROCESSING THREAD
# =====================================================


def process_plate(crop):

    global latest_plate
    global gate_status
    global processing
    global last_detection_time

    try:

        gate_status = "OCR..."

        # =============================================
        # OCR API
        # =============================================

        plate_text = process_ocr(crop)

        if not plate_text:

            gate_status = "OCR FAILED"

            processing = False

            return

        latest_plate = plate_text

        print("PLATE:", plate_text)

        # =============================================
        # RECORD EVENT API
        # =============================================

        gate_status = "CHECKING..."

        result = record_event(
            plate_text,
            crop
        )

        print(result)

        if result and result.get("success"):

            gate_status = "OPEN"

            open_gate()

            last_detection_time = time.time()

        else:

            gate_status = "DENIED"

    except Exception as e:

        print("PROCESS ERROR:", e)

        gate_status = "ERROR"

    processing = False

# =====================================================
# FPS COUNTER
# =====================================================


fps_time = time.time()

fps_counter = 0

fps = 0

print("SYSTEM STARTED")

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    ret, frame = cap.read()

    if not ret:
        continue

    frame_count += 1

    # =================================================
    # FPS
    # =================================================

    fps_counter += 1

    if time.time() - fps_time >= 1:

        fps = fps_counter

        fps_counter = 0

        fps_time = time.time()

    # =================================================
    # DETECTION
    # =================================================

    current_time = time.time()

    detection = detector.detect(frame)

    if detection:

        x1, y1, x2, y2 = detection["bbox"]

        confidence = detection["confidence"]

        # draw bbox
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{confidence:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # =============================================
        # PROCESS EVERY 5 FRAME
        # =============================================

        if (
            frame_count % 5 == 0
            and not processing
            and current_time - last_detection_time > COOLDOWN_SECONDS
        ):

            processing = True

            x1 = max(0, x1)
            y1 = max(0, y1)

            crop = frame[y1:y2, x1:x2]

            if crop.size > 0:

                gate_status = "DETECTED"

                threading.Thread(
                    target=process_plate,
                    args=(crop.copy(),),
                    daemon=True
                ).start()

    # =================================================
    # UI
    # =================================================

    cv2.putText(
        frame,
        f"PLATE: {latest_plate}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"STATUS: {gate_status}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"FPS: {fps}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    cv2.imshow(
        "Parkirkan Scan",
        frame
    )

    key = cv2.waitKey(1)

    if key == ord("q"):
        break

# =====================================================
# CLEANUP
# =====================================================

cap.release()

cv2.destroyAllWindows()