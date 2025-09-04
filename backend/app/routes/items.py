from flask import Blueprint, request, jsonify
from app.matching.item_service import item_service

items_bp = Blueprint('items_bp', __name__)

@items_bp.route('/api/items/all', methods=['GET'])
def get_all_items():
    """Vue.js가 초기에 캐싱할 전체 아이템 목록을 제공하는 API"""
    all_items = item_service.get_all_items_details()
    return jsonify(all_items)

@items_bp.route('/api/items/autocomplete', methods=['GET'])
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

@items_bp.route('/api/items/match', methods=['POST'])
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
        # 서비스에서 딕셔너리를 반환하므로 키로 접근하여 가독성과 안정성을 높입니다.
        return jsonify({
            "query": query, 
            "best_match": result["name"], 
            "score": result["score"],
            "item_id": result["id"]
        })
    else:
        return jsonify({"query": query, "best_match": None, "score": 0}), 404
