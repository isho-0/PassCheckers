# backend/routes/classify.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sku.detect import predict_bbox_with_sku, save_cropped_images
from yolo.detect import predict_name_with_yolo
from db.database_utils import fetch_item_info, insert_image, insert_detected_item
from matching.matcher import map_yolo_name
from PIL import Image
import io
import os

classify_bp = Blueprint("classify", __name__)

def run_detection(img_bytes, conn, image_id, img_width, img_height):
    """
    YOLO + SKU 탐지 후 DB 저장 및 결과 조합.
    """
    print(f"[DETECTION] Starting detection for image_id: {image_id}, size: {img_width}x{img_height}")
    
    # SKU 모델로 바운딩 박스 탐지
    bboxes = predict_bbox_with_sku(img_bytes)
    print(f"[DETECTION] SKU detected {len(bboxes)} bounding boxes")
    
    # YOLO 모델로 객체 분류
    yolo_predictions = predict_name_with_yolo(img_bytes, bboxes)
    print(f"[DETECTION] YOLO classified {len(yolo_predictions)} objects")
    """
    # 크롭 이미지 저장 (성능 개선을 위한 중요한 기능)
    if bboxes:
        try:
            save_cropped_images(img_bytes, bboxes, image_id)
            print(f"[DETECTION] Saved {len(bboxes)} cropped images")
        except Exception as e:
            print(f"[DETECTION WARNING] Failed to save cropped images: {e}")
    """
    enriched_results = []

    for i, p in enumerate(yolo_predictions):
        try:
            item_name_en = map_yolo_name(p["name"])
            db_info = fetch_item_info(item_name_en, conn)
            item_name_ko = db_info["item_name"] if db_info else item_name_en

            insert_detected_item(image_id, item_name_en, item_name_ko, p["bbox"], conn)

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
                "carry_on_allowed": db_info["carry_on_allowed"] if db_info else "정보 없음",
                "checked_baggage_allowed": db_info["checked_baggage_allowed"] if db_info else "정보 없음",
                "notes": db_info["notes"] if db_info else "DB에 규정 정보 없음",
                "notes_EN": db_info["notes_EN"] if db_info else "No regulation information available",
                "source": db_info["source"] if db_info else "unknown"
            })
            
            print(f"[DETECTION] Processed item {i+1}: {item_name_ko} ({item_name_en}) - confidence: {p['confidence']:.2f}")
            
        except Exception as e:
            print(f"[DETECTION ERROR] Failed to process item {i+1}: {e}")
            continue

    print(f"[DETECTION] Detection complete. Found {len(enriched_results)} items")
    return enriched_results


@classify_bp.route("/classify", methods=["POST"])
@jwt_required()
def classify():
    # JWT 토큰에서 사용자 ID 가져오기
    user_id = get_jwt_identity()

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    img_bytes = file.read()

    # 이미지 크기를 먼저 가져옵니다.
    try:
        image = Image.open(io.BytesIO(img_bytes))
        img_width, img_height = image.size
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {e}"}), 400

    try:
        # 데이터베이스 연결 및 트랜잭션 시작
        from db.database_utils import get_db_connection
        conn = get_db_connection()
        
        try:
            # 트랜잭션 시작
            conn.begin()
            
            # 이미지 저장 (JWT에서 얻은 user_id 사용)
            image_id = insert_image(user_id, img_bytes, img_width, img_height, conn)

            # 탐지 및 분류 실행
            results = run_detection(img_bytes, conn, image_id, img_width, img_height)

            # 트랜잭션 커밋
            conn.commit()
            
            return jsonify({
                "message": "Detection and classification complete.",
                "image_id": image_id,
                "image_size": {"width": img_width, "height": img_height},
                "results": results
            })
            
        except Exception as e:
            # 트랜잭션 롤백
            conn.rollback()
            raise e
        finally:
            # 연결 종료
            conn.close()

    except Exception as e:
        print(f"[CLASSIFY ERROR] Image processing failed: {e}")
        print(f"[CLASSIFY ERROR] Error type: {type(e).__name__}")
        import traceback
        print(f"[CLASSIFY ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "이미지 처리 중 오류가 발생했습니다.",
            "details": str(e) if "development" in str(os.environ.get('FLASK_ENV', '')).lower() else "서버 내부 오류"
        }), 500