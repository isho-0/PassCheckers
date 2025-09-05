from flask import Blueprint, request, jsonify
from app.matching.item_service import item_service
from app.models.item_model import ItemModel
from app.models.detected_item_model import DetectedItemModel
from app.services import gemini_service # Gemini 서비스 임포트

items_bp = Blueprint('items_bp', __name__, url_prefix='/api/items')

@items_bp.route('/all', methods=['GET'])
def get_all_items():
    """Vue.js가 초기에 캐싱할 전체 아이템 목록을 제공하는 API"""
    all_items = item_service.get_all_items_details()
    return jsonify(all_items)

@items_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """
    실시간 입력에 대한 자동완성 결과를 제공하는 API
    쿼리 파라미터: ?q=검색어
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "검색어(q)가 필요합니다."}), 400
    
    suggestions = item_service.get_autocomplete_suggestions(query)
    return jsonify(suggestions)

@items_bp.route('/match', methods=['POST'])
def match_item():
    """
    사용자가 최종 입력한 텍스트와 가장 유사한 항목을 찾아주는 API
    """
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "요청 본문에 'query'가 필요합니다."}), 400

    query = data['query']
    result = item_service.find_best_match(query)

    if result:
        return jsonify({
            "query": query, 
            "best_match": result["name"], 
            "score": result["score"],
            "item_id": result["id"]
        })
    else:
        return jsonify({"query": query, "best_match": None, "score": 0}), 404

@items_bp.route('/add', methods=['POST'])
def add_detected_items():
    """새로 추가된 탐지 아이템을 데이터베이스에 저장합니다."""
    data = request.get_json()
    if not data or 'image_id' not in data or 'new_items' not in data:
        return jsonify({"error": "image_id와 new_items가 필요합니다."}), 400

    image_id = data['image_id']
    new_items = data['new_items']

    try:
        for item_data in new_items:
            item_name_ko = item_data['name_ko']
            item_details = ItemModel.get_by_name(item_name_ko)

            if not item_details:
                best_match_result = item_service.find_best_match(item_name_ko)
                if best_match_result and best_match_result['score'] >= 90:
                    print(f"[ADD API] Found similar item '{best_match_result['name']}' for '{item_name_ko}'. Using it.")
                    item_details = ItemModel.get_by_name(best_match_result['name'])

            if not item_details:
                print(f"[ADD API] Item '{item_name_ko}' not found in DB and no high-score match. Calling Gemini...")
                gemini_data = gemini_service.get_item_info_from_gemini(item_name_ko)
                
                if gemini_data:
                    print(f"[ADD API] Gemini returned data for '{item_name_ko}'. Adding to ItemModel...")
                    item_details = ItemModel.add_item_from_api(gemini_data)
                else:
                    print(f"[ADD API] Gemini could not provide data for '{item_name_ko}'. Skipping.")
                    continue

            packing_info = 'none'
            if item_details.carry_on_allowed == '예' and item_details.checked_baggage_allowed == '예':
                packing_info = 'both'
            elif item_details.carry_on_allowed == '예':
                packing_info = 'carry_on'
            elif item_details.checked_baggage_allowed == '예':
                packing_info = 'checked'

            DetectedItemModel.add_item(
                image_id=image_id,
                item_name=item_name_ko,
                item_name_EN=item_details.item_name_EN,
                bbox=item_data['bbox'],
                packing_info=packing_info
            )

        all_detected_items = DetectedItemModel.get_by_image_id(image_id)
        return jsonify([item.to_dict() for item in all_detected_items]), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"[ADD API] Server error: {e}")
        return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

@items_bp.route('/delete', methods=['POST'])
def delete_detected_items():
    """탐지된 아이템들을 데이터베이스에서 삭제하고, 최신 목록을 반환합니다."""
    data = request.get_json()
    if not data or 'item_ids' not in data or 'image_id' not in data:
        return jsonify({"error": "삭제할 item_ids 목록과 image_id가 필요합니다."}), 400

    item_ids_to_delete = data['item_ids']
    image_id = data['image_id']

    try:
        if item_ids_to_delete:
            DetectedItemModel.delete_items(item_ids_to_delete)
        
        all_detected_items = DetectedItemModel.get_by_image_id(image_id)
        return jsonify([item.to_dict() for item in all_detected_items]), 200

    except Exception as e:
        return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

