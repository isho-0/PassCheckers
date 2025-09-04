class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_by_email(self, email):
        cursor = self.db.cursor()
        # 참고: 'password' 컬럼에 암호화된 해시가 저장되어 있다고 가정하고 조회합니다.
        cursor.execute("""
            SELECT user_id, email, password, name, nickname, created_at
            FROM users WHERE email = %s
        """, (email,))
        user_data = cursor.fetchone()
        cursor.close()
        return user_data

    def get_by_user_id(self, user_id):
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT user_id, email, name, nickname, created_at
            FROM users WHERE user_id = %s
        """, (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        return user_data

    def create(self, user_id, email, password_hash, name, nickname):
        cursor = self.db.cursor()
        # 중요: 테이블 스키마의 'password' 컬럼에 보안을 위해 암호화된 해시값을 저장합니다.
        cursor.execute("""
            INSERT INTO users (user_id, email, password, name, nickname, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (user_id, email, password_hash, name, nickname))
        self.db.commit()
        cursor.close()
        return user_id