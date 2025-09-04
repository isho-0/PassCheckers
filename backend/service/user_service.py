import bcrypt
from repository.user_repo import UserRepository

class UserExistsException(Exception): pass
class InvalidCredentialsException(Exception): pass

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, user_id, email, password, name, nickname):
        # 사용자가 입력한 ID가 이미 존재하는지 확인
        if self.user_repo.get_by_user_id(user_id):
            raise UserExistsException('이미 존재하는 아이디입니다')
        # 이메일 중복 확인
        if self.user_repo.get_by_email(email):
            raise UserExistsException('이미 존재하는 이메일입니다')
        
        # 보안을 위해 비밀번호는 암호화하여 저장
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # user_repo.create는 이제 user_id를 직접 받음
        self.user_repo.create(user_id, email, hashed_pw, name, nickname)
        
        # 생성된 사용자 정보 반환
        user = self.user_repo.get_by_user_id(user_id)
        return user

    def login(self, email, password):
        user = self.user_repo.get_by_email(email)
        # 'password_hash' 대신 스키마에 정의된 'password' 컬럼을 사용
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            raise InvalidCredentialsException('잘못된 이메일 또는 비밀번호입니다')
        
        return user