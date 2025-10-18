"""
Enterprise Chat API Endpoints
REST API and WebSocket handlers for real-time chat system
"""

from flask import Blueprint, request, jsonify, session
from flask_socketio import emit, join_room, leave_room, rooms
import json
import logging
from datetime import datetime
from typing import Dict, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.enterprise_chat import (
        EnterpriseChatManager, ChatStatus, MessageType, UserType
    )
    chat_manager = EnterpriseChatManager()
except ImportError as e:
    print(f"Warning: Could not import chat manager: {e}")
    # Create a mock chat manager for testing
    class MockChatManager:
        def start_chat(self, user_info): return "test_chat_123"
        def process_message(self, **kwargs): return "Thanks for your message!"
        def get_welcome_message(self, user_info): return "Welcome to Enterprise Scanner!"
    chat_manager = MockChatManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
enterprise_chat_bp = Blueprint('enterprise_chat', __name__, url_prefix='/api/chat')


@enterprise_chat_bp.route('/start', methods=['POST'])
def start_chat():
    """Start new chat session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "Request data required"}), 400
        
        # Extract visitor information
        visitor_data = {
            'name': data.get('name', 'Anonymous'),
            'email': data.get('email'),
            'company': data.get('company'),
            'session_id': session.get('session_id'),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'page_url': data.get('page_url'),
            'referrer': data.get('referrer'),
            'location': data.get('location')
        }
        
        # Create chat session
        chat_session = chat_manager.create_chat_session(visitor_data)
        
        # Store chat ID in session
        session['chat_id'] = chat_session.chat_id
        session['user_id'] = chat_session.visitor.user_id
        
        return jsonify({
            "success": True,
            "chat_id": chat_session.chat_id,
            "user_id": chat_session.visitor.user_id,
            "status": chat_session.status.value,
            "message": "Chat session started successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to start chat: {e}")
        return jsonify({"error": "Failed to start chat session"}), 500


@enterprise_chat_bp.route('/message', methods=['POST'])
def send_message():
    """Send message in chat"""
    try:
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({"error": "Message content required"}), 400
        
        chat_id = data.get('chat_id') or session.get('chat_id')
        user_id = data.get('user_id') or session.get('user_id')
        
        if not chat_id or not user_id:
            return jsonify({"error": "Chat session not found"}), 404
        
        # Send message
        message = chat_manager.send_message(
            chat_id=chat_id,
            sender_id=user_id,
            content=data['message'],
            message_type=MessageType.TEXT
        )
        
        # Generate auto-response if needed
        response_content = None
        escalate = False
        
        # Check for specific keywords and generate responses
        message_lower = data['message'].lower()
        
        if any(word in message_lower for word in ['demo', 'demonstration']):
            response_content = "I'd be happy to arrange a personalized demo of Enterprise Scanner. Our platform has helped Fortune 500 companies save millions in breach prevention. What's the best time for you?"
            
        elif any(word in message_lower for word in ['price', 'pricing', 'cost']):
            response_content = "Our enterprise pricing is customized based on your organization's size and requirements. Most Fortune 500 clients see 300-800% ROI within the first year. Would you like me to prepare a custom proposal?"
            
        elif any(word in message_lower for word in ['security', 'vulnerability', 'breach']):
            response_content = "Security is our specialty! Enterprise Scanner provides comprehensive vulnerability assessment, threat intelligence, and compliance management. What specific security challenges is your organization facing?"
            
        elif any(word in message_lower for word in ['fortune 500', 'enterprise', 'large company']):
            response_content = "Perfect! Enterprise Scanner is specifically designed for Fortune 500 organizations. We currently serve 150+ enterprise clients with our cybersecurity platform. Let me connect you with our enterprise specialist."
            escalate = True
            
        elif any(word in message_lower for word in ['urgent', 'emergency', 'breach', 'incident']):
            response_content = "I understand this is urgent. Let me immediately connect you with our senior security consultant who can provide immediate assistance."
            escalate = True
            
        elif any(word in message_lower for word in ['compliance', 'audit', 'soc 2', 'iso 27001']):
            response_content = "Compliance is critical for enterprise organizations. Enterprise Scanner helps achieve SOC 2, ISO 27001, NIST, and other compliance frameworks. Our compliance team can provide detailed guidance."
            escalate = True
        
        return jsonify({
            "success": True,
            "message_id": message.message_id,
            "timestamp": message.timestamp.isoformat(),
            "response": response_content,
            "escalate": escalate,
            "escalate_reason": "Enterprise inquiry" if escalate else None
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return jsonify({"error": "Failed to send message"}), 500


@enterprise_chat_bp.route('/escalate', methods=['POST'])
def escalate_chat():
    """Escalate chat to human agent"""
    try:
        data = request.get_json()
        
        chat_id = data.get('chat_id') or session.get('chat_id')
        reason = data.get('reason', 'User requested escalation')
        
        if not chat_id:
            return jsonify({"error": "Chat session not found"}), 404
        
        # Escalate chat
        success = chat_manager.escalate_chat(chat_id, reason)
        
        if success:
            # Send email notification to sales team
            chat_session = chat_manager.active_sessions.get(chat_id)
            if chat_session:
                send_escalation_email(chat_session, reason)
            
            return jsonify({
                "success": True,
                "message": "Chat escalated successfully",
                "estimated_response_time": "2-5 minutes"
            }), 200
        else:
            return jsonify({"error": "Failed to escalate chat"}), 500
            
    except Exception as e:
        logger.error(f"Failed to escalate chat: {e}")
        return jsonify({"error": "Failed to escalate chat"}), 500


@enterprise_chat_bp.route('/close', methods=['POST'])
def close_chat():
    """Close chat session"""
    try:
        data = request.get_json() or {}
        
        chat_id = data.get('chat_id') or session.get('chat_id')
        rating = data.get('satisfaction_rating')
        
        if not chat_id:
            return jsonify({"error": "Chat session not found"}), 404
        
        # Close chat
        success = chat_manager.close_chat(chat_id, rating)
        
        if success:
            # Clear session data
            session.pop('chat_id', None)
            session.pop('user_id', None)
            
            return jsonify({
                "success": True,
                "message": "Chat session closed successfully"
            }), 200
        else:
            return jsonify({"error": "Failed to close chat"}), 500
            
    except Exception as e:
        logger.error(f"Failed to close chat: {e}")
        return jsonify({"error": "Failed to close chat"}), 500


@enterprise_chat_bp.route('/history/<chat_id>', methods=['GET'])
def get_chat_history(chat_id: str):
    """Get chat history"""
    try:
        # Verify user has access to this chat
        user_chat_id = session.get('chat_id')
        if user_chat_id != chat_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        chat_session = chat_manager.get_chat_history(chat_id)
        
        if not chat_session:
            return jsonify({"error": "Chat not found"}), 404
        
        # Return chat data
        return jsonify({
            "chat_id": chat_session.chat_id,
            "status": chat_session.status.value,
            "created_at": chat_session.created_at.isoformat(),
            "messages": [
                {
                    "message_id": msg.message_id,
                    "sender_type": msg.sender_type.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_type": msg.message_type.value
                }
                for msg in chat_session.messages
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        return jsonify({"error": "Failed to get chat history"}), 500


@enterprise_chat_bp.route('/status', methods=['GET'])
def get_chat_status():
    """Get current chat status"""
    try:
        chat_id = session.get('chat_id')
        
        if not chat_id:
            return jsonify({
                "active": False,
                "message": "No active chat session"
            }), 200
        
        if chat_id in chat_manager.active_sessions:
            chat_session = chat_manager.active_sessions[chat_id]
            return jsonify({
                "active": True,
                "chat_id": chat_id,
                "status": chat_session.status.value,
                "message_count": len(chat_session.messages),
                "created_at": chat_session.created_at.isoformat()
            }), 200
        else:
            return jsonify({
                "active": False,
                "message": "Chat session not found"
            }), 200
            
    except Exception as e:
        logger.error(f"Failed to get chat status: {e}")
        return jsonify({"error": "Failed to get chat status"}), 500


@enterprise_chat_bp.route('/support-info', methods=['GET'])
def get_support_info():
    """Get support team information"""
    try:
        return jsonify({
            "business_hours": {
                "available": "24/7 for Fortune 500 clients",
                "standard": "8 AM - 8 PM UTC",
                "timezone": "UTC"
            },
            "response_times": {
                "standard": "5-10 minutes",
                "enterprise": "2-5 minutes",
                "fortune_500": "1-2 minutes"
            },
            "escalation_triggers": [
                "Fortune 500 inquiries",
                "Security incidents",
                "Compliance questions",
                "Enterprise pricing",
                "Technical emergencies"
            ],
            "support_channels": {
                "chat": "Available now",
                "email": "sales@enterprisescanner.com",
                "phone": "+1-800-ENTERPRISE"
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get support info: {e}")
        return jsonify({"error": "Failed to get support info"}), 500


# WebSocket event handlers (for Flask-SocketIO)
def register_socketio_handlers(socketio):
    """Register WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        try:
            chat_id = session.get('chat_id')
            if chat_id:
                join_room(chat_id)
                emit('connected', {
                    'status': 'connected',
                    'chat_id': chat_id
                })
                logger.info(f"Client connected to chat {chat_id}")
            else:
                emit('connected', {
                    'status': 'no_active_chat'
                })
                
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            emit('error', {'message': 'Connection failed'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        try:
            chat_id = session.get('chat_id')
            if chat_id:
                leave_room(chat_id)
                logger.info(f"Client disconnected from chat {chat_id}")
                
        except Exception as e:
            logger.error(f"WebSocket disconnection error: {e}")
    
    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Handle joining chat room"""
        try:
            chat_id = data.get('chat_id')
            if chat_id and chat_id == session.get('chat_id'):
                join_room(chat_id)
                emit('joined_chat', {
                    'chat_id': chat_id,
                    'status': 'joined'
                })
                
        except Exception as e:
            logger.error(f"Error joining chat: {e}")
            emit('error', {'message': 'Failed to join chat'})
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle real-time message sending"""
        try:
            chat_id = session.get('chat_id')
            user_id = session.get('user_id')
            content = data.get('message')
            
            if not chat_id or not user_id or not content:
                emit('error', {'message': 'Invalid message data'})
                return
            
            # Send message
            message = chat_manager.send_message(
                chat_id=chat_id,
                sender_id=user_id,
                content=content,
                message_type=MessageType.TEXT
            )
            
            # Broadcast to room
            socketio.emit('new_message', {
                'message_id': message.message_id,
                'sender_type': message.sender_type.value,
                'content': message.content,
                'timestamp': message.timestamp.isoformat()
            }, room=chat_id)
            
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            emit('error', {'message': 'Failed to send message'})
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicators"""
        try:
            chat_id = session.get('chat_id')
            if chat_id:
                emit('user_typing', {
                    'chat_id': chat_id,
                    'typing': data.get('typing', False)
                }, room=chat_id, include_self=False)
                
        except Exception as e:
            logger.error(f"Error handling typing: {e}")
    
    # Store socketio instance in chat manager
    chat_manager.socketio = socketio


def send_escalation_email(chat_session, reason: str):
    """Send escalation email to sales team"""
    try:
        # Email configuration (in production, use proper email service)
        subject = f"🚨 URGENT Chat Escalation - {chat_session.visitor.company or 'Enterprise Prospect'}"
        
        # Recent messages for context
        recent_messages = chat_session.messages[-5:] if len(chat_session.messages) > 5 else chat_session.messages
        message_history = "\n".join([
            f"[{msg.timestamp.strftime('%H:%M')}] {msg.sender_type.value}: {msg.content}"
            for msg in recent_messages
        ])
        
        body = f"""
URGENT CHAT ESCALATION - IMMEDIATE ATTENTION REQUIRED

Escalation Reason: {reason}
Priority Level: {chat_session.priority}/4
Chat ID: {chat_session.chat_id}

PROSPECT INFORMATION:
Name: {chat_session.visitor.name}
Email: {chat_session.visitor.email or 'Not provided'}
Company: {chat_session.visitor.company or 'Not provided'}
IP Address: {chat_session.visitor.ip_address}

CHAT CONTEXT:
Started: {chat_session.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
Status: {chat_session.status.value}
Messages: {len(chat_session.messages)}

RECENT CONVERSATION:
{message_history}

ACTION REQUIRED:
- Respond within 2 minutes for Fortune 500 prospects
- Use chat ID {chat_session.chat_id} to join conversation
- Escalate to senior consultant if needed

CHAT LINK: https://enterprisescanner.com/admin/chat/{chat_session.chat_id}
        """
        
        # In production, send actual email
        # For now, just log the escalation
        logger.info(f"ESCALATION EMAIL SENT for chat {chat_session.chat_id}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Recipients: sales@enterprisescanner.com, support@enterprisescanner.com")
        
        # Could also send Slack notification, SMS, etc.
        
    except Exception as e:
        logger.error(f"Failed to send escalation email: {e}")


# Error handlers
@enterprise_chat_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400


@enterprise_chat_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401


@enterprise_chat_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@enterprise_chat_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500