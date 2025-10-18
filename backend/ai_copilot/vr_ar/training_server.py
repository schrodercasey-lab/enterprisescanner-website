"""
JUPITER VR/AR Platform - VR Training Server (Module G.3.11)

WebSocket + REST API server for VR training and certification system.
Provides training scenarios, skill assessment, and practice environments.

WebSocket Events (Port 5011):
- training_progress: Real-time progress updates
- step_completed: Step completion notifications
- skill_assessed: Skill assessment results
- certification_earned: Certification notifications

REST API Endpoints:
- GET /api/scenarios: List available training scenarios
- POST /api/start-scenario: Start a training scenario
- GET /api/current-step: Get current training step
- POST /api/complete-step: Complete a training step
- POST /api/use-hint: Request a hint
- POST /api/skip-step: Skip optional step
- GET /api/progress: Get user progress
- POST /api/assess-skills: Assess user skills
- POST /api/practice-session: Create practice environment
- POST /api/practice-action: Execute practice action
- GET /api/health: Health check

Enterprise Scanner - JUPITER Platform
October 2025
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
from typing import Dict, List
import threading

from training_system import (
    TrainingScenarioManager,
    SkillAssessment,
    PracticeSimulator,
    TrainingScenario,
    SkillLevel,
    TrainingStepType
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jupiter-vr-training-secret-2025'
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global training system components
scenario_manager = TrainingScenarioManager()
skill_assessment = SkillAssessment()
practice_simulator = PracticeSimulator()

# Connected clients
connected_clients: Dict[str, Dict] = {}


# ============================================================================
# WebSocket Event Handlers
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients[client_id] = {
        'connected_at': time.time(),
        'user_id': None,
        'active_scenario': None
    }
    
    emit('connected', {
        'client_id': client_id,
        'server_time': time.time(),
        'available_scenarios': len(scenario_manager.scenarios)
    })
    
    print(f"Training client connected: {client_id}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]
    
    print(f"Training client disconnected: {client_id}")


@socketio.on('register_user')
def handle_register_user(data):
    """Register user for training"""
    client_id = request.sid
    user_id = data.get('user_id')
    
    if client_id in connected_clients:
        connected_clients[client_id]['user_id'] = user_id
    
    emit('user_registered', {
        'success': True,
        'user_id': user_id,
        'timestamp': time.time()
    })
    
    print(f"User registered: {user_id}")


@socketio.on('start_scenario')
def handle_start_scenario(data):
    """Start a training scenario"""
    client_id = request.sid
    user_id = data.get('user_id')
    scenario_id = data.get('scenario_id')
    
    try:
        progress = scenario_manager.start_scenario(user_id, scenario_id)
        scenario = scenario_manager.get_scenario(scenario_id)
        current_step = scenario_manager.get_current_step(user_id, scenario_id)
        
        if client_id in connected_clients:
            connected_clients[client_id]['active_scenario'] = scenario_id
        
        emit('scenario_started', {
            'success': True,
            'scenario_id': scenario_id,
            'scenario_title': scenario.title if scenario else '',
            'total_steps': len(scenario.steps) if scenario else 0,
            'current_step': {
                'step_id': current_step.step_id,
                'title': current_step.title,
                'description': current_step.description,
                'instructions': current_step.instructions,
                'points': current_step.points,
                'time_limit': current_step.time_limit_seconds
            } if current_step else None,
            'timestamp': time.time()
        })
        
        # Broadcast to other clients (for collaboration)
        socketio.emit('training_started', {
            'user_id': user_id,
            'scenario_id': scenario_id,
            'timestamp': time.time()
        }, skip_sid=client_id)
        
        print(f"Scenario started: {scenario_id} for user {user_id}")
    
    except Exception as e:
        emit('scenario_started', {
            'success': False,
            'error': str(e)
        })


@socketio.on('complete_step')
def handle_complete_step(data):
    """Complete a training step"""
    client_id = request.sid
    user_id = data.get('user_id')
    scenario_id = data.get('scenario_id')
    step_id = data.get('step_id')
    score = data.get('score', 0)
    actions_taken = data.get('actions_taken', [])
    
    try:
        result = scenario_manager.complete_step(
            user_id,
            scenario_id,
            step_id,
            score,
            actions_taken
        )
        
        # Get next step if available
        next_step = None
        if result['success'] and not result.get('scenario_complete', False):
            current_step = scenario_manager.get_current_step(user_id, scenario_id)
            if current_step:
                next_step = {
                    'step_id': current_step.step_id,
                    'title': current_step.title,
                    'description': current_step.description,
                    'instructions': current_step.instructions,
                    'points': current_step.points,
                    'time_limit': current_step.time_limit_seconds
                }
        
        emit('step_completed', {
            **result,
            'next_step': next_step,
            'timestamp': time.time()
        })
        
        # Broadcast progress update
        socketio.emit('training_progress', {
            'user_id': user_id,
            'scenario_id': scenario_id,
            'step_completed': step_id,
            'total_score': result.get('total_score', 0),
            'timestamp': time.time()
        })
        
        # Check for certification
        if result.get('scenario_complete') and result.get('passed'):
            socketio.emit('certification_earned', {
                'user_id': user_id,
                'scenario_id': scenario_id,
                'score': result.get('total_score', 0),
                'timestamp': time.time()
            })
        
        print(f"Step completed: {step_id} by user {user_id}, score: {score}")
    
    except Exception as e:
        emit('step_completed', {
            'success': False,
            'error': str(e)
        })


@socketio.on('request_hint')
def handle_request_hint(data):
    """Request a hint for current step"""
    client_id = request.sid
    user_id = data.get('user_id')
    scenario_id = data.get('scenario_id')
    
    hint = scenario_manager.use_hint(user_id, scenario_id)
    
    emit('hint_provided', {
        'success': hint is not None,
        'hint': hint,
        'timestamp': time.time()
    })
    
    if hint:
        print(f"Hint provided to user {user_id}")


@socketio.on('skip_step')
def handle_skip_step(data):
    """Skip an optional step"""
    user_id = data.get('user_id')
    scenario_id = data.get('scenario_id')
    step_id = data.get('step_id')
    
    result = scenario_manager.skip_step(user_id, scenario_id, step_id)
    
    # Get next step
    next_step = None
    if result.get('success'):
        current_step = scenario_manager.get_current_step(user_id, scenario_id)
        if current_step:
            next_step = {
                'step_id': current_step.step_id,
                'title': current_step.title,
                'description': current_step.description,
                'instructions': current_step.instructions
            }
    
    emit('step_skipped', {
        **result,
        'next_step': next_step,
        'timestamp': time.time()
    })


@socketio.on('assess_skills')
def handle_assess_skills(data):
    """Assess user skills"""
    user_id = data.get('user_id')
    
    # Get completed scenarios
    completed = []
    if user_id in scenario_manager.user_progress:
        for scenario_id, progress in scenario_manager.user_progress[user_id].items():
            if progress.completed_at:
                completed.append(progress)
    
    assessment = skill_assessment.assess_user(user_id, completed)
    
    emit('skills_assessed', {
        'success': True,
        'skill_level': assessment.skill_level.value,
        'overall_score': assessment.overall_score,
        'strengths': assessment.strengths,
        'weaknesses': assessment.weaknesses,
        'recommended_scenarios': [s.value for s in assessment.recommended_scenarios],
        'category_scores': assessment.category_scores,
        'timestamp': time.time()
    })
    
    # Broadcast skill level achievement
    socketio.emit('skill_assessed', {
        'user_id': user_id,
        'skill_level': assessment.skill_level.value,
        'timestamp': time.time()
    })
    
    print(f"Skills assessed for user {user_id}: {assessment.skill_level.value}")


@socketio.on('start_practice')
def handle_start_practice(data):
    """Start a practice session"""
    user_id = data.get('user_id')
    scenario_type = data.get('scenario_type')
    
    try:
        scenario_enum = TrainingScenario[scenario_type.upper()]
        session = practice_simulator.create_practice_environment(user_id, scenario_enum)
        
        emit('practice_started', {
            'success': True,
            'session_id': session['session_id'],
            'scenario_type': session['scenario_type'],
            'threats': session['threats'],
            'timestamp': time.time()
        })
        
        print(f"Practice session started: {session['session_id']}")
    
    except Exception as e:
        emit('practice_started', {
            'success': False,
            'error': str(e)
        })


@socketio.on('practice_action')
def handle_practice_action(data):
    """Execute action in practice environment"""
    session_id = data.get('session_id')
    action = data.get('action')
    parameters = data.get('parameters', {})
    
    result = practice_simulator.execute_practice_action(session_id, action, parameters)
    
    emit('action_executed', {
        **result,
        'timestamp': time.time()
    })


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'jupiter-vr-training',
        'timestamp': time.time(),
        'connected_clients': len(connected_clients),
        'available_scenarios': len(scenario_manager.scenarios)
    })


@app.route('/api/scenarios', methods=['GET'])
def list_scenarios():
    """List available training scenarios"""
    difficulty = request.args.get('difficulty')
    
    skill_level = None
    if difficulty:
        try:
            skill_level = SkillLevel[difficulty.upper()]
        except KeyError:
            pass
    
    scenarios = scenario_manager.list_scenarios(skill_level)
    
    return jsonify({
        'scenarios': [
            {
                'scenario_id': s.scenario_id,
                'title': s.title,
                'description': s.description,
                'difficulty': s.difficulty.value,
                'duration_minutes': s.estimated_duration_minutes,
                'steps_count': len(s.steps),
                'total_points': s.total_points,
                'pass_threshold': s.pass_threshold_percent,
                'learning_objectives': s.learning_objectives,
                'prerequisites': s.prerequisites
            }
            for s in scenarios
        ],
        'count': len(scenarios)
    })


@app.route('/api/scenario/<scenario_id>', methods=['GET'])
def get_scenario_details(scenario_id):
    """Get detailed scenario information"""
    scenario = scenario_manager.get_scenario(scenario_id)
    
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404
    
    return jsonify({
        'scenario_id': scenario.scenario_id,
        'title': scenario.title,
        'description': scenario.description,
        'difficulty': scenario.difficulty.value,
        'duration_minutes': scenario.estimated_duration_minutes,
        'total_points': scenario.total_points,
        'pass_threshold': scenario.pass_threshold_percent,
        'learning_objectives': scenario.learning_objectives,
        'prerequisites': scenario.prerequisites,
        'steps': [
            {
                'step_id': step.step_id,
                'type': step.step_type.value,
                'title': step.title,
                'description': step.description,
                'points': step.points,
                'required': step.required,
                'time_limit': step.time_limit_seconds
            }
            for step in scenario.steps
        ]
    })


@app.route('/api/start-scenario', methods=['POST'])
def start_scenario():
    """Start a training scenario"""
    data = request.get_json()
    user_id = data.get('user_id')
    scenario_id = data.get('scenario_id')
    
    if not user_id or not scenario_id:
        return jsonify({'error': 'Missing user_id or scenario_id'}), 400
    
    try:
        progress = scenario_manager.start_scenario(user_id, scenario_id)
        scenario = scenario_manager.get_scenario(scenario_id)
        current_step = scenario_manager.get_current_step(user_id, scenario_id)
        
        return jsonify({
            'success': True,
            'scenario_id': scenario_id,
            'started_at': progress.started_at.isoformat(),
            'current_step': {
                'step_id': current_step.step_id,
                'title': current_step.title,
                'description': current_step.description,
                'instructions': current_step.instructions,
                'expected_actions': current_step.expected_actions,
                'points': current_step.points,
                'time_limit': current_step.time_limit_seconds
            } if current_step else None
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/current-step', methods=['GET'])
def get_current_step():
    """Get current training step"""
    user_id = request.args.get('user_id')
    scenario_id = request.args.get('scenario_id')
    
    if not user_id or not scenario_id:
        return jsonify({'error': 'Missing user_id or scenario_id'}), 400
    
    current_step = scenario_manager.get_current_step(user_id, scenario_id)
    
    if not current_step:
        return jsonify({'error': 'No active step'}), 404
    
    return jsonify({
        'step_id': current_step.step_id,
        'type': current_step.step_type.value,
        'title': current_step.title,
        'description': current_step.description,
        'instructions': current_step.instructions,
        'expected_actions': current_step.expected_actions,
        'points': current_step.points,
        'required': current_step.required,
        'time_limit': current_step.time_limit_seconds,
        'hints_available': len(current_step.hints)
    })


@app.route('/api/complete-step', methods=['POST'])
def complete_step():
    """Complete a training step"""
    data = request.get_json()
    user_id = data.get('user_id')
    scenario_id = data.get('scenario_id')
    step_id = data.get('step_id')
    score = data.get('score', 0)
    actions_taken = data.get('actions_taken', [])
    
    result = scenario_manager.complete_step(
        user_id,
        scenario_id,
        step_id,
        score,
        actions_taken
    )
    
    return jsonify(result)


@app.route('/api/use-hint', methods=['POST'])
def use_hint():
    """Request a hint"""
    data = request.get_json()
    user_id = data.get('user_id')
    scenario_id = data.get('scenario_id')
    
    hint = scenario_manager.use_hint(user_id, scenario_id)
    
    return jsonify({
        'success': hint is not None,
        'hint': hint
    })


@app.route('/api/skip-step', methods=['POST'])
def skip_step():
    """Skip an optional step"""
    data = request.get_json()
    user_id = data.get('user_id')
    scenario_id = data.get('scenario_id')
    step_id = data.get('step_id')
    
    result = scenario_manager.skip_step(user_id, scenario_id, step_id)
    
    return jsonify(result)


@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get user progress"""
    user_id = request.args.get('user_id')
    scenario_id = request.args.get('scenario_id')
    
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    
    if scenario_id:
        # Get progress for specific scenario
        progress = scenario_manager.get_progress(user_id, scenario_id)
        if not progress:
            return jsonify({'error': 'No progress found'}), 404
        
        return jsonify({
            'scenario_id': progress.scenario_id,
            'started_at': progress.started_at.isoformat(),
            'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
            'current_step_index': progress.current_step_index,
            'completed_steps': progress.completed_steps,
            'skipped_steps': progress.skipped_steps,
            'total_score': progress.total_score,
            'hints_used': progress.hints_used,
            'time_spent_seconds': progress.time_spent_seconds,
            'passed': progress.passed
        })
    else:
        # Get all progress for user
        all_progress = scenario_manager.user_progress.get(user_id, {})
        
        return jsonify({
            'user_id': user_id,
            'scenarios': [
                {
                    'scenario_id': p.scenario_id,
                    'completed': p.completed_at is not None,
                    'score': p.total_score,
                    'passed': p.passed,
                    'time_spent': p.time_spent_seconds
                }
                for p in all_progress.values()
            ],
            'total_completed': sum(1 for p in all_progress.values() if p.completed_at),
            'total_score': sum(p.total_score for p in all_progress.values())
        })


@app.route('/api/assess-skills', methods=['POST'])
def assess_skills():
    """Assess user skills"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    
    # Get completed scenarios
    completed = []
    if user_id in scenario_manager.user_progress:
        for scenario_id, progress in scenario_manager.user_progress[user_id].items():
            if progress.completed_at:
                completed.append(progress)
    
    assessment = skill_assessment.assess_user(user_id, completed)
    
    return jsonify({
        'user_id': assessment.user_id,
        'assessed_at': assessment.assessed_at.isoformat(),
        'skill_level': assessment.skill_level.value,
        'overall_score': assessment.overall_score,
        'category_scores': assessment.category_scores,
        'strengths': assessment.strengths,
        'weaknesses': assessment.weaknesses,
        'recommended_scenarios': [s.value for s in assessment.recommended_scenarios]
    })


@app.route('/api/assessment-history', methods=['GET'])
def get_assessment_history():
    """Get assessment history"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    
    history = skill_assessment.get_assessment_history(user_id)
    
    return jsonify({
        'user_id': user_id,
        'assessments': [
            {
                'assessed_at': a.assessed_at.isoformat(),
                'skill_level': a.skill_level.value,
                'overall_score': a.overall_score,
                'category_scores': a.category_scores
            }
            for a in history
        ],
        'count': len(history)
    })


@app.route('/api/practice-session', methods=['POST'])
def create_practice_session():
    """Create practice environment"""
    data = request.get_json()
    user_id = data.get('user_id')
    scenario_type = data.get('scenario_type')
    
    if not user_id or not scenario_type:
        return jsonify({'error': 'Missing user_id or scenario_type'}), 400
    
    try:
        scenario_enum = TrainingScenario[scenario_type.upper()]
        session = practice_simulator.create_practice_environment(user_id, scenario_enum)
        
        return jsonify({
            'success': True,
            'session_id': session['session_id'],
            'scenario_type': session['scenario_type'],
            'created_at': session['created_at'].isoformat(),
            'threats': session['threats']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/practice-action', methods=['POST'])
def execute_practice_action():
    """Execute action in practice environment"""
    data = request.get_json()
    session_id = data.get('session_id')
    action = data.get('action')
    parameters = data.get('parameters', {})
    
    if not session_id or not action:
        return jsonify({'error': 'Missing session_id or action'}), 400
    
    result = practice_simulator.execute_practice_action(session_id, action, parameters)
    
    return jsonify(result)


@app.route('/api/practice-summary', methods=['POST'])
def end_practice_session():
    """End practice session and get summary"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
    
    summary = practice_simulator.end_practice_session(session_id)
    
    return jsonify(summary)


# ============================================================================
# Server Initialization
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("JUPITER VR Training Server")
    print("=" * 70)
    print(f"Starting server on port 5011...")
    print(f"WebSocket: ws://localhost:5011")
    print(f"REST API: http://localhost:5011/api/")
    print(f"Training scenarios: {len(scenario_manager.scenarios)}")
    print("=" * 70)
    
    # Run server
    socketio.run(app, host='0.0.0.0', port=5011, debug=False, allow_unsafe_werkzeug=True)
