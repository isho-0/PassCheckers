# app/routes/classify.py
from flask import Blueprint, request, jsonify
from app.sku.detect import predict_bbox_with_sku, save_cropped_images
from app.yolo.detect import predict_name_with_yolo
from app.db.database import get_engine, fetch_item_info, insert_image, insert_detected_item
from app.matching.matcher import map_yolo_name

classify_bp = Blueprint("classify", __name__)

def run_detection(img_bytes, conn, image_id):
    """
    YOLO + SKU 탐지 후 DB 저장 및 결과 조합
    """
    bboxes = predict_bbox_with_sku(img_bytes)

    # 테스트용 코드
    save_cropped_images(img_bytes, bboxes, image_id)
    yolo_predictions = predict_name_with_yolo(img_bytes, bboxes)

    enriched_results = []

    for p in yolo_predictions:
        # 1️⃣ YOLO → DB 이름 매핑
        item_name_en = map_yolo_name(p["name"])

        # 2️⃣ DB 조회
        db_info = fetch_item_info(item_name_en)
        item_name_ko = db_info["item_name"] if db_info else item_name_en

        # 3️⃣ 탐지 결과 DB 저장
        insert_detected_item(conn, image_id, item_name_en, item_name_ko, p["bbox"])

        # 4️⃣ 결과 조합
        enriched_results.append({
            "name_ko": item_name_ko,
            "name_en": item_name_en,
            "bbox": p["bbox"],
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

    engine = get_engine()
    if not engine:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with engine.begin() as conn:
            # --- 이미지 저장 ---
            image_id = insert_image(conn, user_id="custom1", image_bytes=img_bytes)

            # --- 탐지 + DB 저장 + 결과 조합 ---
            results = run_detection(img_bytes, conn, image_id)

            return jsonify({
                "message": "Detection and classification complete.",
                "image_id": image_id,
                "results": results
            })

    except Exception as e:
        print(f"Error during image processing: {e}")
        return jsonify({"error": str(e)}), 500
