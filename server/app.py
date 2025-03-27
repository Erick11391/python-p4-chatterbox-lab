from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Message
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enhanced CORS Configuration
CORS(app, resources={
    r"/messages*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

db.init_app(app)

# Health Check Endpoint
@app.route('/')
def health_check():
    return jsonify({
        "status": "running",
        "message": "Chatterbox API is ready",
        "endpoints": {
            "messages": "/messages",
            "health": "/health"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Improved Message Endpoints
@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([message.to_dict() for message in messages])
    except Exception as e:
        app.logger.error(f"Error fetching messages: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/messages', methods=['POST'])
def create_message():
    try:
        data = request.get_json()
        if not data or 'body' not in data or 'username' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        message = Message(
            body=data['body'],
            username=data['username']
        )
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating message: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    try:
        message = db.session.get(Message, id)
        if not message:
            return jsonify({"error": "Message not found"}), 404
        
        data = request.get_json()
        if 'body' not in data:
            return jsonify({"error": "Missing body field"}), 400
            
        message.body = data['body']
        db.session.commit()
        return jsonify(message.to_dict())
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating message: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    try:
        message = db.session.get(Message, id)
        if not message:
            return jsonify({"error": "Message not found"}), 404
        
        db.session.delete(message)
        db.session.commit()
        return jsonify({"success": True, "message": "Message deleted"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting message: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Request Logging Middleware
@app.after_request
def after_request(response):
    """Log request details"""
    app.logger.info(
        f"{request.method} {request.path} - {response.status_code}"
    )
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)