# backend/matching/item_service.py

from models.item_model import ItemModel
from models.detected_item_model import DetectedItemModel
from services import gemini_service
from rapidfuzz import process, fuzz
import threading
import time

class ItemService:
    """물품 매칭 및 검색 서비스를 제공하는 클래스"""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ItemService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._cached_items = []
        self.item_names = []
        self._name_to_id_map = {}
        self._last_cache_update = 0
        self.cache_interval = 3600  # 1시간 (초 단위)
        self._initialized = True
        self._load_cache()

    def _load_cache(self):
        """매칭용 아이템 데이터를 불러옵니다."""
        try:
            self._cached_items = ItemModel.get_all_for_caching()
            self.item_names = [item['item_name'] for item in self._cached_items]
            self._name_to_id_map = {item['item_name']: item['id'] for item in self._cached_items}
            self._last_cache_update = time.time()
            print(f"✅ Item service cache loaded. Total items: {len(self._cached_items)}")
        except Exception as e:
            print(f"Error loading items cache: {e}")
            self._cached_items = []
            self.item_names = []
            self._name_to_id_map = {}

    def _check_and_refresh_cache(self):
        """캐시 만료 여부를 확인하고 필요하면 새로고침합니다."""
        if time.time() - self._last_cache_update > self.cache_interval:
            self._load_cache()

    def get_all_items_details(self):
        """프론트엔드 초기화를 위해 모든 아이템의 상세 정보를 DB에서 직접 조회합니다."""
        self._check_and_refresh_cache()
        return ItemModel.get_all_details()
    
    def get_autocomplete_suggestions(self, query, limit=5):
        """자동완성을 위한 물품명 제안을 반환합니다."""
        if not query:
            return []

        self._check_and_refresh_cache()
        
        results = process.extract(query, self.item_names, scorer=fuzz.WRatio, limit=limit, score_cutoff=75)

        return [result[0] for result in results]
    
    def find_best_match(self, query, threshold=30):
        """입력된 쿼리와 가장 유사한 물품을 찾습니다."""
        if not query:
            return None

        self._check_and_refresh_cache()
        
        result = process.extractOne(query, self.item_names, scorer=fuzz.WRatio, score_cutoff=threshold)
        if result:
            match_name, score, _ = result
            item_id = self._name_to_id_map.get(match_name)
            return {
                "name": match_name,
                "score": round(score, 2),
                "id": item_id
            }
        return None

    def update_detected_item(self, item_id, new_name_ko, new_bbox):
        """탐지된 아이템의 이름 및/또는 bbox를 업데이트합니다."""
        detected_item = DetectedItemModel.get_by_id(item_id)
        if not detected_item:
            raise ValueError(f"Detected item with id {item_id} not found.")

        updates = {}
        if new_bbox and new_bbox != detected_item.get('bbox'):
            updates['bbox'] = new_bbox

        # 이름이 변경된 경우, 새 물품 정보를 찾아야 합니다.
        if new_name_ko and new_name_ko != detected_item.get('item_name'):
            updates['name_ko'] = new_name_ko
            
            # 1. 새 이름으로 items 테이블에서 조회
            item_details = ItemModel.get_by_name(new_name_ko)

            # 2. 없으면, 유사한 이름으로 조회
            if not item_details:
                best_match_result = self.find_best_match(new_name_ko)
                if best_match_result and best_match_result['score'] >= 90:
                    item_details = ItemModel.get_by_name(best_match_result['name'])

            # 3. 그래도 없으면, Gemini API 호출
            if not item_details:
                print(f"[Update Service] Item '{new_name_ko}' not found. Calling Gemini...")
                gemini_data = gemini_service.get_item_info_from_gemini(new_name_ko)
                if gemini_data and 'item_data' in gemini_data and 'weight_data' in gemini_data:
                    item_details = ItemModel.add_item_from_api(
                        gemini_data['item_data'], 
                        gemini_data['weight_data']
                    )
                    # 캐시 새로고침
                    self._load_cache()
                else:
                    # Gemini 실패 시, 업데이트를 중단하거나 기본값으로 처리할 수 있습니다.
                    # 여기서는 일단 이름만 업데이트하고 나머지 정보는 비우는 것으로 처리합니다.
                    print(f"[Update Service] Gemini failed for '{new_name_ko}'. Updating name only.")
                    updates['item_name_EN'] = ''
                    updates['packing_info'] = 'none'
                    DetectedItemModel.update_details(item_id, updates)
                    return

            # 새 물품 정보로 업데이트할 내용을 설정합니다.
            if item_details:
                packing_info = 'none'
                carry_on = item_details.get('carry_on_allowed', '아니요')
                checked = item_details.get('checked_baggage_allowed', '아니요')
                if carry_on.startswith('예') and checked.startswith('예'):
                    packing_info = 'both'
                elif carry_on.startswith('예'):
                    packing_info = 'carry_on'
                elif checked.startswith('예'):
                    packing_info = 'checked'
                
                updates['item_name_EN'] = item_details.get('item_name_EN')
                updates['packing_info'] = packing_info

        # 변경 사항이 있을 경우에만 DB 업데이트를 수행합니다.
        if updates:
            DetectedItemModel.update_details(item_id, updates)

# 싱글톤 인스턴스
item_service = ItemService()