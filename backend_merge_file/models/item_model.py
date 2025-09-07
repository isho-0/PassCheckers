from app.db.database import db

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

    @classmethod
    def get_by_name(cls, item_name):
        """이름으로 특정 아이템의 상세 정보를 조회합니다."""
        return cls.query.filter_by(item_name=item_name).first()

    @classmethod
    def add_item_from_api(cls, item_data):
        """API (Gemini)로부터 받은 데이터를 기반으로 새 아이템을 추가합니다."""
        # 허용된 값 목록
        allowed_carry_on = ["예", "아니요", "예 (특별 지침)", "예 (3.4oz/100 ml 이상 또는 동일)"]
        allowed_checked = ["예", "아니요", "예 (특별 지침)"]

        # 데이터 유효성 검사 및 기본값 설정
        carry_on = item_data.get('carry_on_allowed', '아니요')
        checked = item_data.get('checked_baggage_allowed', '아니요')

        # 허용된 값에 없는 경우 기본값으로 대체
        if carry_on not in allowed_carry_on:
            carry_on = '아니요'
        if checked not in allowed_checked:
            checked = '아니요'

        new_item = cls(
            item_name=item_data['item_name'],
            item_name_EN=item_data.get('item_name_EN'),
            carry_on_allowed=carry_on,
            checked_baggage_allowed=checked,
            notes=item_data.get('notes'),
            notes_EN=item_data.get('notes_EN'),
            source='API' # Gemini API를 통해 추가된 항목임을 명시
        )
        db.session.add(new_item)
        db.session.commit()
        return new_item

    def to_dict(self):
        """Converts this model instance to a dictionary."""
        return {
            'id': self.id,
            'item_name': self.item_name,
            'item_name_EN': self.item_name_EN,
            'carry_on_allowed': self.carry_on_allowed,
            'checked_baggage_allowed': self.checked_baggage_allowed,
            'notes': self.notes,
            'notes_EN': self.notes_EN,
            'source': self.source
        }

    @classmethod
    def get_by_id(cls, item_id):
        """ID로 특정 아이템의 상세 정보를 조회합니다."""
        return cls.query.get(item_id)