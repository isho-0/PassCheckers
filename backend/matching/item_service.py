# backend/matching/item_service.py

from models.item_model import ItemModel
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
        
        # WRatio 스코어 75점 이상인 항목만 반환하도록 score_cutoff 값을 상향 조정합니다.
        # limit은 여전히 5로 유지하여, 최대 5개의 가장 유사한 항목만 가져옵니다.
        results = process.extract(query, self.item_names, scorer=fuzz.WRatio, limit=limit, score_cutoff=75)

        # 결과는 (찾은문자열, 점수, 인덱스) 튜플의 리스트이므로, 문자열만 추출합니다.
        return [result[0] for result in results]
    
    def find_best_match(self, query, threshold=30):
        """입력된 쿼리와 가장 유사한 물품을 찾습니다."""
        if not query:
            return None

        self._check_and_refresh_cache()
        
        # 가장 유사한 항목 1개를 찾습니다.
        result = process.extractOne(query, self.item_names, scorer=fuzz.WRatio, score_cutoff=threshold)
        if result:
            match_name, score, _ = result  # score는 0-100 스케일
            # 캐시된 맵을 사용해 ID를 즉시 찾습니다.
            item_id = self._name_to_id_map.get(match_name)
            return {
                "name": match_name,
                "score": round(score, 2),
                "id": item_id
            }
        return None

# 싱글톤 인스턴스
item_service = ItemService()