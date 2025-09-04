from app import db

class ItemModel(db.Model):
    """
    데이터베이스의 'items' 테이블에 매핑되는 SQLAlchemy 모델 클래스입니다.
    """
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False, unique=True)
    item_name_EN = db.Column(db.String(255))
    carry_on_allowed = db.Column(db.String(50))
    checked_baggage_allowed = db.Column(db.String(50))
    notes = db.Column(db.Text)
    notes_EN = db.Column(db.Text)
    source = db.Column(db.String(50))

    @classmethod
    def get_all_for_caching(cls):
        """매칭 서비스 캐싱을 위해 id와 이름만 조회합니다."""
        items = cls.query.with_entities(cls.id, cls.item_name).all()
        # SQLAlchemy Core Row 객체를 dict로 변환
        return [{'id': item.id, 'item_name': item.item_name} for item in items]

    @classmethod
    def get_all_details(cls):
        """프론트엔드에서 사용할 모든 아이템 상세 정보를 조회합니다."""
        items = cls.query.all()
        return [
            {
                'id': item.id, 'item_name': item.item_name, 'item_name_EN': item.item_name_EN,
                'carry_on_allowed': item.carry_on_allowed, 'checked_baggage_allowed': item.checked_baggage_allowed,
                'notes': item.notes, 'notes_EN': item.notes_EN, 'source': item.source
            } for item in items
        ]

    def __repr__(self):
        return f"<ItemModel {self.item_name}>"