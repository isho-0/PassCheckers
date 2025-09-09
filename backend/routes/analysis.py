# backend/routes/analysis.py
from flask import Blueprint, request, jsonify
from db.database_utils import get_db_connection
from datetime import datetime
import json
import os

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/api/analysis/save", methods=["POST"])
def save_analysis_results():
    """분석 결과를 데이터베이스에 저장합니다."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다."}), 400
        
        required_fields = ['user_id', 'image_id', 'detected_items', 'total_items']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"필수 필드가 누락되었습니다: {field}"}), 400
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 분석 결과 테이블이 없으면 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(50) NOT NULL,
                        image_id INT NOT NULL,
                        image_url TEXT,
                        image_width INT,
                        image_height INT,
                        total_items INT NOT NULL,
                        analysis_date DATETIME NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 분석된 물품 상세 테이블이 없으면 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        analysis_id INT NOT NULL,
                        item_name_ko VARCHAR(255) NOT NULL,
                        item_name_en VARCHAR(255),
                        confidence DECIMAL(5,4),
                        carry_on_allowed VARCHAR(100),
                        checked_baggage_allowed VARCHAR(100),
                        notes TEXT,
                        notes_EN TEXT,
                        source VARCHAR(50),
                        bbox_x_min DECIMAL(10,8),
                        bbox_y_min DECIMAL(10,8),
                        bbox_x_max DECIMAL(10,8),
                        bbox_y_max DECIMAL(10,8),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 분석 결과 저장
                # ISO 형식의 날짜를 MySQL datetime 형식으로 변환
                analysis_date = data.get('analysis_date', datetime.now().isoformat())
                if 'T' in analysis_date:
                    # ISO 형식에서 MySQL datetime 형식으로 변환
                    analysis_date = analysis_date.replace('T', ' ').replace('Z', '').split('.')[0]
                
                cursor.execute("""
                    INSERT INTO analysis_results 
                    (user_id, image_id, image_url, image_width, image_height, total_items, analysis_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['user_id'],
                    data['image_id'],
                    data.get('image_url', ''),
                    data.get('image_size', {}).get('width', 0),
                    data.get('image_size', {}).get('height', 0),
                    data['total_items'],
                    analysis_date
                ))
                
                analysis_id = cursor.lastrowid
                
                # 분석된 물품들 저장
                for item in data['detected_items']:
                    bbox = item.get('bbox', [0, 0, 0, 0])
                    cursor.execute("""
                        INSERT INTO analysis_items 
                        (analysis_id, item_name_ko, item_name_en, confidence, 
                         carry_on_allowed, checked_baggage_allowed, notes, notes_EN, source,
                         bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        analysis_id,
                        item.get('name_ko', ''),
                        item.get('name_en', ''),
                        item.get('confidence', 0),
                        item.get('carry_on_allowed', ''),
                        item.get('checked_baggage_allowed', ''),
                        item.get('notes', ''),
                        item.get('notes_EN', ''),
                        item.get('source', ''),
                        bbox[0] if len(bbox) > 0 else 0,
                        bbox[1] if len(bbox) > 1 else 0,
                        bbox[2] if len(bbox) > 2 else 0,
                        bbox[3] if len(bbox) > 3 else 0
                    ))
                
                conn.commit()
                
                return jsonify({
                    "message": "분석 결과가 성공적으로 저장되었습니다.",
                    "analysis_id": analysis_id,
                    "total_items": data['total_items']
                })
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        print(f"[ANALYSIS SAVE ERROR] {e}")
        return jsonify({
            "error": "분석 결과 저장 중 오류가 발생했습니다.",
            "details": str(e) if "development" in str(os.environ.get('FLASK_ENV', '')).lower() else "서버 내부 오류"
        }), 500

@analysis_bp.route("/api/analysis/history/<user_id>", methods=["GET"])
def get_analysis_history(user_id):
    """사용자의 분석 기록을 조회합니다."""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT ar.id, ar.image_id, ar.image_url, ar.total_items, 
                           ar.analysis_date, ar.created_at
                    FROM analysis_results ar
                    WHERE ar.user_id = %s
                    ORDER BY ar.created_at DESC
                    LIMIT 50
                """, (user_id,))
                
                results = cursor.fetchall()
                
                return jsonify({
                    "message": "분석 기록을 성공적으로 조회했습니다.",
                    "results": results
                })
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"[ANALYSIS HISTORY ERROR] {e}")
        return jsonify({
            "error": "분석 기록 조회 중 오류가 발생했습니다.",
            "details": str(e) if "development" in str(os.environ.get('FLASK_ENV', '')).lower() else "서버 내부 오류"
        }), 500

@analysis_bp.route("/api/analysis/detail/<int:analysis_id>", methods=["GET"])
def get_analysis_detail(analysis_id):
    """특정 분석 결과의 상세 정보를 조회합니다."""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 분석 결과 기본 정보
                cursor.execute("""
                    SELECT ar.*, i.width, i.height
                    FROM analysis_results ar
                    LEFT JOIN images i ON ar.image_id = i.id
                    WHERE ar.id = %s
                """, (analysis_id,))
                
                analysis_info = cursor.fetchone()
                if not analysis_info:
                    return jsonify({"error": "분석 결과를 찾을 수 없습니다."}), 404
                
                # 분석된 물품들
                cursor.execute("""
                    SELECT * FROM analysis_items
                    WHERE analysis_id = %s
                    ORDER BY id
                """, (analysis_id,))
                
                items = cursor.fetchall()
                
                # bbox 정보를 배열로 변환
                for item in items:
                    item['bbox'] = [
                        float(item['bbox_x_min']),
                        float(item['bbox_y_min']),
                        float(item['bbox_x_max']),
                        float(item['bbox_y_max'])
                    ]
                
                return jsonify({
                    "message": "분석 상세 정보를 성공적으로 조회했습니다.",
                    "analysis": analysis_info,
                    "items": items
                })
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"[ANALYSIS DETAIL ERROR] {e}")
        return jsonify({
            "error": "분석 상세 정보 조회 중 오류가 발생했습니다.",
            "details": str(e) if "development" in str(os.environ.get('FLASK_ENV', '')).lower() else "서버 내부 오류"
        }), 500
