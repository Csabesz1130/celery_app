from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.utils
import json
from .models import Session, TaskResult

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/task_stats')
def task_stats():
    session = Session()
    try:
        # Utolsó 24 óra adatai
        last_24h = datetime.utcnow() - timedelta(hours=24)
        results = session.query(TaskResult).filter(TaskResult.created_at >= last_24h).all()
        
        # Átalakítás DataFrame-be
        df = pd.DataFrame([{
            'task_name': r.task_name,
            'status': r.status,
            'created_at': r.created_at
        } for r in results])
        
        if not df.empty:
            # Sikerességi arányok
            success_rates = df.groupby('task_name')['status'].apply(
                lambda x: (x == 'success').mean() * 100
            ).round(2).to_dict()
            
            # Időbeli trend
            df['hour'] = df['created_at'].dt.hour
            hourly_stats = df.groupby(['task_name', 'hour', 'status']).size().unstack(fill_value=0)
            hourly_stats = hourly_stats.reset_index()
            
            fig = px.line(hourly_stats, x='hour', y='success', color='task_name',
                         title='Feladatok sikerességi aránya óránként',
                         labels={'hour': 'Óra', 'success': 'Sikeres futások', 'task_name': 'Feladat'})
            
            return jsonify({
                'success_rates': success_rates,
                'chart_data': json.loads(fig.to_json())
            })
        return jsonify({'success_rates': {}, 'chart_data': None})
    finally:
        session.close()

@app.route('/api/recent_tasks')
def recent_tasks():
    session = Session()
    try:
        tasks = session.query(TaskResult).order_by(TaskResult.created_at.desc()).limit(10).all()
        return jsonify([{
            'task_name': t.task_name,
            'status': t.status,
            'result': t.result,
            'error_message': t.error_message,
            'created_at': t.created_at.isoformat()
        } for t in tasks])
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True) 