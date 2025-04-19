from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TaskResult(db.Model):
    __tablename__ = 'task_results'
    
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success' or 'failure'
    result = db.Column(db.String(255))
    error_message = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TaskResult(task_name='{self.task_name}', status='{self.status}')>" 