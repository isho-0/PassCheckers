# app/routes/classify.py
from flask import Blueprint, request, jsonify
from app.sku.detect import predict_bbox_with_sku, save_cropped_images
from app.yolo.detect import predict_name_with_yolo
from app.db.database import get_engine, fetch_item_info, insert_image, insert_detected_item
from app.matching.matcher import map_yolo_name
from PIL import Image
import io

classify_bp = Blueprint("classify", __name__)

def run_detection(img_bytes, conn, image_id, img_width, img_height):
    """
    YOLO + SKU 탐지 후 DB 저장 및 결과 조합.
    (수정됨: 이미지 크기를 인자로 받음)
    """
    bboxes = predict_bbox_with_sku(img_bytes)
    yolo_predictions = predict_name_with_yolo(img_bytes, bboxes)

    enriched_results = []

    for p in yolo_predictions:
        item_name_en = map_yolo_name(p["name"])
        db_info = fetch_item_info(item_name_en)
        item_name_ko = db_info["item_name"] if db_info else item_name_en

        insert_detected_item(conn, image_id, item_name_en, item_name_ko, p["bbox"])

        x_min, y_min, x_max, y_max = p["bbox"]
        normalized_bbox = [
            x_min / img_width,
            y_min / img_height,
            x_max / img_width,
            y_max / img_height
        ]

        enriched_results.append({
            "name_ko": item_name_ko,
            "name_en": item_name_en,
            "bbox": normalized_bbox,
            "confidence": p["confidence"],
            "carry_on_allowed": db_info["carry_on_allowed"] if db_info else None,
            "checked_baggage_allowed": db_info["checked_baggage_allowed"] if db_info else None,
            "notes": db_info["notes"] if db_info else "DB에 규정 정보 없음"
        })

    return enriched_results


@classify_bp.route("/classify", methods=["POST"])
def classify():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    img_bytes = file.read()

    # (수정됨) 이미지 크기를 먼저 가져옵니다.
    try:
        image = Image.open(io.BytesIO(img_bytes))
        img_width, img_height = image.size
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {e}"}), 400

    engine = get_engine()
    if not engine:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with engine.begin() as conn:
            # (수정됨) 이미지 저장 시 크기 정보 전달
            image_id = insert_image(conn, user_id="custom1", image_bytes=img_bytes, width=img_width, height=img_height)

            # (수정됨) 탐지 함수에 크기 정보 전달
            results = run_detection(img_bytes, conn, image_id, img_width, img_height)

            return jsonify({
                "message": "Detection and classification complete.",
                "image_id": image_id,
                "image_size": {"width": img_width, "height": img_height},
                "results": results
            })

    except Exception as e:
        print(f"Error during image processing: {e}")
        return jsonify({"error": str(e)}), 500
