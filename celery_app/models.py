from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class TaskResult(Base):
    __tablename__ = 'task_results'
    
    id = Column(Integer, primary_key=True)
    task_name = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # 'success' or 'failure'
    result = Column(String(255))
    error_message = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TaskResult(task_name='{self.task_name}', status='{self.status}')>"

# Adatbázis kapcsolat létrehozása
engine = create_engine('sqlite:///tasks.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine) 