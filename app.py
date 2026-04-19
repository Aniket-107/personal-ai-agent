from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from ai_service import process_ai_message
from calendar_service import add_calendar_event
from task_service import get_tasks, add_task, update_task_status

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/ai', methods=['POST'])
def ai_endpoint():
    data = request.get_json()
    message = data.get('message', '')
    result = process_ai_message(message)
    return jsonify(result)

@app.route('/calendar/events', methods=['GET'])
def get_events():
    return jsonify({"events": []})

@app.route('/calendar/events', methods=['POST'])
def create_event():
    data = request.get_json()
    result = add_calendar_event(
        title=data.get('title', ''),
        description=data.get('description', ''),
        event_time=data.get('event_time', '')
    )
    return jsonify(result)

@app.route('/tasks', methods=['GET'])
def list_tasks():
    return jsonify({"tasks": get_tasks()})

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    result = add_task(data.get('title', ''))
    return jsonify(result)

@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    data = request.get_json()
    result = update_task_status(task_id, data.get('status', 'todo'))
    return jsonify(result)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)