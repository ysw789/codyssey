"""
프로젝트 실행 진입점

이 파일은 프로젝트의 메인 실행 파일입니다.
프로젝트 실행 시 데이터베이스 테이블 생성 여부를 확인하고 생성합니다.
"""
from database import engine
from models import Base

if __name__ == '__main__':
    """
    메인 실행 흐름:
    
    1. 모듈 import 단계
       - database.py에서 engine import (SQLite 연결 엔진)
       - models.py에서 Base import (모든 모델의 메타데이터 포함)
    
    2. 테이블 생성 단계
       - Base.metadata.create_all(bind=engine) 실행
       - 동작: Base.metadata에 등록된 모든 모델(Question)을 확인
       - 동작: 데이터베이스에 해당 테이블이 없으면 생성, 있으면 스킵
       - 주의: Alembic을 사용하는 경우 이 방법보다는 마이그레이션을 사용하는 것이 권장됨
    
    3. 완료 메시지 출력
       - 테이블 생성 완료 후 사용자에게 알림
    """
    # 테이블 생성 확인
    # 동작: models.py에 정의된 모든 모델의 테이블을 데이터베이스에 생성합니다.
    # 이미 테이블이 존재하는 경우 아무 작업도 수행하지 않습니다.
    Base.metadata.create_all(bind=engine)
    print('데이터베이스 테이블이 생성되었습니다.')
