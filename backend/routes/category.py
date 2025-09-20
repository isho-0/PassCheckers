# backend/routes/category.py
from flask import Blueprint, request, jsonify
from services.gemini_service import get_and_update_categories

category_bp = Blueprint("category", __name__)

@category_bp.route("/api/categorize", methods=["POST"])
def categorize_items():
    """물품 목록을 받아 카테고리를 분류하고 결과를 반환합니다."""
    data = request.get_json()
    if not data or 'item_names' not in data or not isinstance(data['item_names'], list):
        return jsonify({"error": "요청 형식이 올바르지 않습니다. 'item_names' 필드가 리스트 형태로 필요합니다."}), 400

    item_names = data['item_names']
    
    try:
        categories = get_and_update_categories(item_names)
        return jsonify({
            "message": "카테고리 분류를 성공적으로 완료했습니다.",
            "categories": categories
        })
    except Exception as e:
        print(f"[CATEGORIZE API ERROR] {e}")
        return jsonify({
            "error": "카테고리 분류 중 오류가 발생했습니다.",
            "details": str(e)
        }), 500
