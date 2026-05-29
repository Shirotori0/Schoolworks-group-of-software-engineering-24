from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库连接配置（和 .env 里的值保持一致）
MYSQL_USER = "root"
MYSQL_PASSWORD = "456852"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DATABASE = "emotion_system"

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """每次请求获取一个数据库会话，用完关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()