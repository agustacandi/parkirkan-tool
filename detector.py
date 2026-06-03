import cv2
import numpy as np
import onnxruntime as ort

from config import (
    MODEL_PATH,
    INPUT_SIZE,
    CONFIDENCE_THRESHOLD
)


class PlateDetector:

    def __init__(self):

        print("Loading ONNX model...")

        self.session = ort.InferenceSession(
            MODEL_PATH,
            providers=["CPUExecutionProvider"]
        )

        self.input_name = self.session.get_inputs()[0].name

        print("Model loaded!")

    def detect(self, frame):

        image = cv2.resize(frame, (INPUT_SIZE, INPUT_SIZE))

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        input_image = image_rgb.astype(np.float32) / 255.0

        input_image = np.transpose(input_image, (2, 0, 1))

        input_image = np.expand_dims(input_image, axis=0)

        outputs = self.session.run(
            None,
            {self.input_name: input_image}
        )

        output = outputs[0]

        if len(output.shape) == 3:
            output = output[0]

        detections = output.T

        best_conf = 0
        best_box = None

        for det in detections:

            conf = det[4]

            if conf > best_conf and conf > CONFIDENCE_THRESHOLD:

                x, y, w, h = det[:4]

                best_conf = conf

                best_box = [x, y, w, h]

        if best_box is None:
            return None

        x, y, w, h = best_box

        frame_h, frame_w = frame.shape[:2]

        scale_x = frame_w / INPUT_SIZE
        scale_y = frame_h / INPUT_SIZE

        x1 = int((x - w / 2) * scale_x)
        y1 = int((y - h / 2) * scale_y)

        x2 = int((x + w / 2) * scale_x)
        y2 = int((y + h / 2) * scale_y)

        return {
            "bbox": (x1, y1, x2, y2),
            "confidence": float(best_conf)
        }