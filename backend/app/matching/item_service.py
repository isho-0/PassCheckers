from app.models.item_model import ItemModel
from rapidfuzz import process, fuzz

class ItemsService:
    def __init__(self):
        # __init__에서는 캐시를 비어있는 상태로 초기화만 합니다.
        # 실제 데이터 로딩은 init_app에서 수행됩니다.
        self._cached_items = []
        self.item_names = []
        self._name_to_id_map = {}

    def init_app(self, app):
        """
        Flask 앱 컨텍스트 내에서 데이터베이스 의존성을 초기화합니다.
        이 메서드는 create_app 팩토리 함수에서 호출되어야 합니다.
        """
        with app.app_context():
            self._cached_items = self._load_items_for_matching()
            self.item_names = [item['item_name'] for item in self._cached_items]
            self._name_to_id_map = {item['item_name']: item['id'] for item in self._cached_items}
            print("✅ Item service cache initialized successfully.")

    def _load_items_for_matching(self):
        """매칭용 아이템 데이터를 불러옵니다."""
        return ItemModel.get_all_for_caching()
    
    def get_all_items_details(self):
        """프론트엔드 초기화를 위해 모든 아이템의 상세 정보를 DB에서 직접 조회합니다."""
        # 이 데이터는 크기가 클 수 있으므로, 요청 시에만 DB에서 가져옵니다.
        return ItemModel.get_all_details()
    
    def get_autocomplete_suggestions(self, query, limit=5):
        if not query:
            return []
        
        # rapidfuzz를 사용하여 더 빠르고 정확하게 유사 항목을 찾습니다.
        # cutoff는 0-100 사이의 점수입니다.
        results = process.extract(query, self.item_names, scorer=fuzz.WRatio, limit=limit, score_cutoff=30)
        # 결과는 (찾은문자열, 점수, 인덱스) 튜플의 리스트이므로, 문자열만 추출합니다.
        return [result[0] for result in results]
    
    def find_best_match(self, query):
        # 가장 유사한 항목 1개를 찾습니다.
        result = process.extractOne(query, self.item_names, scorer=fuzz.WRatio, score_cutoff=30)
        if result:
            match_name, score, _ = result # score는 0-100 스케일
            # 캐시된 맵을 사용해 ID를 즉시 찾습니다.
            item_id = self._name_to_id_map.get(match_name)
            return {
                "name": match_name,
                "score": round(score, 2),
                "id": item_id
            }
        return None
    
# 싱글톤 인스턴스
item_service = ItemsService()
