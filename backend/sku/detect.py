# backend/sku/detect.py

import os
from PIL import Image
import io
from ultralytics import YOLO  # YOLO 모델을 사용하기 위해 import
from ultralytics.nn.tasks import DetectionModel
import torch

# PyTorch 2.6+ 호환성을 위한 safe globals 설정
torch.serialization.add_safe_globals([DetectionModel])

# SKU 모델 경로 설정 (절대 경로 사용)
SKU_MODEL_PATH = os.path.join(os.getcwd(), "models", "pytorch", "SKU_model.pt")

# SKU 모델 인스턴스 생성 (YOLO 클래스 사용)
# 이 시점에서 모델 파일이 로드됩니다.
try:
    sku_model = YOLO(SKU_MODEL_PATH)
    print(f"SKU model loaded successfully from {SKU_MODEL_PATH}")
except Exception as e:
    print(f"Error loading SKU model: {e}")
    sku_model = None


def predict_bbox_with_sku(image_data: bytes, conf_threshold: float = 0.10):
    """
    BLOB 이미지 데이터를 받아 SKU 모델로 바운딩 박스를 탐지하고 목록을 반환합니다.
    conf_threshold: 탐지 임계값 (기본 0.10)
    """
    if sku_model is None:
        print("SKU model is not loaded. Cannot perform prediction.")
        return []

    try:
        results = sku_model(
            Image.open(io.BytesIO(image_data)),
            conf=conf_threshold  # 여기서 임계값 지정
        )

        bboxes = []
        if results and results[0].boxes:
            for box in results[0].boxes:
                bbox = box.xyxy[0].tolist()
                bboxes.append(bbox)

        return bboxes
    except Exception as e:
        print(f"Error in SKU prediction: {e}")
        return []


def save_cropped_images(image_data: bytes, bboxes: list, image_id: int):
    """
    SKU 모델이 탐지한 바운딩 박스에 맞춰 이미지를 잘라내고 저장합니다.
    """
    # 저장 경로 설정
    RESULT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'results'))
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    
    # 원본 이미지 로드
    original_image = Image.open(io.BytesIO(image_data))
    
    for i, bbox in enumerate(bboxes):
        try:
            # 바운딩 박스 좌표로 이미지 크롭
            cropped_image = original_image.crop(bbox)
            
            # 파일명 형식: {image_id}_cropped_{인덱스}.jpg
            save_path = os.path.join(RESULT_FOLDER, f"{image_id}_cropped_{i}.jpg")
            
            cropped_image.save(save_path, 'JPEG')
            print(f"Cropped image saved to {save_path}")
        except Exception as e:
            print(f"Error saving cropped image for bbox {i}: {e}")
