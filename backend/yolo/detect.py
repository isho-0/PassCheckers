# backend/yolo/detect.py

import os
from ultralytics import YOLO
from PIL import Image
import torch
import io
from ultralytics.nn.tasks import DetectionModel

# PyTorch 2.6+ 호환성을 위한 safe globals 설정
torch.serialization.add_safe_globals([DetectionModel])

# YOLO 모델 경로 설정 (절대 경로 사용)
YOLO_MODEL_PATH = os.path.join(os.getcwd(), "models", "pytorch", "YOLOv11_model.pt")

# YOLO 모델 인스턴스 생성
try:
    yolo_model = YOLO(YOLO_MODEL_PATH)
    print(f"YOLO model loaded successfully from {YOLO_MODEL_PATH}")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    yolo_model = None


def predict_name_with_yolo(image_data: bytes, bboxes: list):
    """
    BLOB 이미지 데이터와 바운딩 박스 목록을 받아 YOLO 모델로 객체 이름을 분류합니다.
    """
    if yolo_model is None:
        print("YOLO model is not loaded. Cannot perform prediction.")
        return []

    # BLOB 데이터를 PIL Image 객체로 변환
    image = Image.open(io.BytesIO(image_data))

    final_predictions = []

    for bbox in bboxes:
        # 바운딩 박스 영역을 잘라냄
        cropped_image = image.crop(bbox)

        # 잘라낸 이미지를 YOLO 모델에 입력하여 객체 이름 분류
        yolo_results = yolo_model(cropped_image)

        if yolo_results and yolo_results[0].boxes:
            # YOLO가 탐지한 객체 중 가장 높은 confidence를 가진 결과를 선택
            best_yolo_detection = yolo_results[0].boxes[0]
            cls_id = int(best_yolo_detection.cls[0])
            item_name_en = yolo_model.names.get(cls_id, f"Unknown_{cls_id}")
            confidence = float(best_yolo_detection.conf[0])

            final_predictions.append({
                'name': item_name_en,
                'bbox': bbox,
                'confidence': confidence
            })

    return final_predictions
