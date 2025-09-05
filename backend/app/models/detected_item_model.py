from app.db.database import db

class DetectedItemModel(db.Model):
    """
    데이터베이스의 'detected_items' 테이블에 매핑되는 SQLAlchemy 모델 클래스입니다.
    """
    __tablename__ = 'detected_items'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_id = db.Column(db.Integer, nullable=False)
    item_name_EN = db.Column(db.String(255), nullable=True)
    item_name = db.Column(db.String(255), nullable=False)
    bbox_x_min = db.Column(db.Float, nullable=False)
    bbox_y_min = db.Column(db.Float, nullable=False)
    bbox_x_max = db.Column(db.Float, nullable=False)
    bbox_y_max = db.Column(db.Float, nullable=False)
    # packing_info는 현재 스키마에 따라 문자열로 처리, 필요시 Enum으로 변경 가능
    packing_info = db.Column(db.String(50), default='none')

    @classmethod
    def add_item(cls, image_id, item_name, bbox, item_name_EN=None, packing_info='none'):
        """새로운 탐지 아이템을 데이터베이스에 추가합니다."""
        if not all([image_id, item_name, bbox and len(bbox) == 4]):
            raise ValueError("필수 인자(image_id, item_name, bbox)가 누락되었거나 형식이 잘못되었습니다.")

        new_item = cls(
            image_id=image_id,
            item_name=item_name,
            item_name_EN=item_name_EN,
            bbox_x_min=bbox[0],
            bbox_y_min=bbox[1],
            bbox_x_max=bbox[2],
            bbox_y_max=bbox[3],
            packing_info=packing_info
        )
        db.session.add(new_item)
        db.session.commit()
        return new_item

    def to_dict(self):
        """객체 데이터를 딕셔너리로 변환합니다."""
        return {
            'item_id': self.item_id,
            'image_id': self.image_id,
            'item_name': self.item_name,
            'item_name_EN': self.item_name_EN,
            'bbox': [self.bbox_x_min, self.bbox_y_min, self.bbox_x_max, self.bbox_y_max],
            'packing_info': self.packing_info
        }

    def __repr__(self):
        return f"<DetectedItemModel {self.item_id}: {self.item_name}>"

    @classmethod
    def delete_items(cls, item_ids):
        """ID 목록을 받아 여러 탐지 아이템을 삭제합니다."""
        if not item_ids:
            return 0
        
        try:
            num_deleted = cls.query.filter(cls.item_id.in_(item_ids)).delete(synchronize_session=False)
            db.session.commit()
            return num_deleted
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_by_image_id(cls, image_id):
        """특정 이미지 ID에 해당하는 모든 탐지 아이템을 조회합니다."""
        return cls.query.filter_by(image_id=image_id).all()
