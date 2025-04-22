from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.utils
import json
import os
from .models import db, TaskResult

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Adatbázis létrehozása
with app.app_context():
    db.create_all()
    print("Adatbázis táblák létrehozva")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/task_stats')
def task_stats():
    try:
        last_24h = datetime.utcnow() - timedelta(hours=24)
        results = TaskResult.query.filter(TaskResult.created_at >= last_24h).all()
        
        df = pd.DataFrame([{
            'task_name': r.task_name,
            'status': r.status,
            'created_at': r.created_at
        } for r in results])
        
        if not df.empty:
            
            success_rates = df.groupby('task_name')['status'].apply(
                lambda x: (x == 'success').mean() * 100
            ).round(2).to_dict()
            
            
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
    except Exception as e:
        app.logger.error(f"Error in task_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent_tasks')
def recent_tasks():
    try:
        tasks = TaskResult.query.order_by(TaskResult.created_at.desc()).limit(10).all()
        return jsonify([{
            'task_name': t.task_name,
            'status': t.status,
            'result': t.result,
            'error_message': t.error_message,
            'created_at': t.created_at.isoformat()
        } for t in tasks])
    except Exception as e:
        app.logger.error(f"Error in recent_tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True) 