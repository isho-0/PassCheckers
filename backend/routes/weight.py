# backend/routes/weight.py
from flask import Blueprint, jsonify
from services.gemini_predict import get_predicted_weights_for_analysis

weight_bp = Blueprint("weight", __name__)

def convert_to_grams(value, unit):
    """단위를 그램(g)으로 변환합니다."""
    if unit.lower() == 'kg':
        return value * 1000
    return value

@weight_bp.route("/api/weight/predict/<int:analysis_id>", methods=["GET"])
def predict_weights(analysis_id):
    """특정 분석 ID에 대한 무게 예측을 처리하고 총 무게를 계산합니다."""
    try:
        # gemini_predict 서비스 호출
        items_with_weights = get_predicted_weights_for_analysis(analysis_id)

        if items_with_weights is None or "error" in items_with_weights:
            error_message = items_with_weights.get("error", "An unknown error occurred") if isinstance(items_with_weights, dict) else "An unknown error occurred"
            return jsonify({"error": "무게 예측 중 오류가 발생했습니다.", "details": error_message}), 500

        total_weight_grams = 0
        simplified_items = []
        for item in items_with_weights:
            value = item.get('predicted_weight_value')
            unit = item.get('predicted_weight_unit')
            
            # 총 무게 계산
            if value is not None and unit is not None:
                total_weight_grams += convert_to_grams(float(value), unit)
            
            # 응답을 위한 아이템 리스트 간소화
            simplified_items.append({
                "item_name_ko": item.get("item_name_ko"),
                "predicted_weight_value": item.get("predicted_weight_value"),
                "predicted_weight_unit": item.get("predicted_weight_unit")
            })
        
        # 총 무게를 kg으로 변환
        total_weight_kg = round(total_weight_grams / 1000, 2)

        return jsonify({
            "message": "무게 예측 및 계산이 성공적으로 완료되었습니다.",
            "analysis_id": analysis_id,
            "items": simplified_items,
            "total_weight_kg": total_weight_kg
        })

    except Exception as e:
        print(f"[WEIGHT PREDICT ROUTE ERROR] {e}")
        return jsonify({
            "error": "요청 처리 중 서버 오류가 발생했습니다.",
            "details": str(e)
        }), 500
