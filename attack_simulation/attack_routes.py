from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from attack_simulation.attack_service import run_simulation
from logs.logger import log_event

attack_bp = Blueprint('attacks', __name__)


@attack_bp.route('/simulate', methods=['POST'])
@jwt_required()
def simulate_attack():
    username = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    attack_type = data.get('attack_type')

    result = run_simulation(attack_type)
    log_event(
        username,
        f"Attack Simulation: {result['attack_type']} [{result['severity']}]",
        result['status']
    )

    status_code = 400 if result['status'] == 'REJECTED' else 200
    return jsonify({
        "attack_type": result['attack_type'],
        "severity": result['severity'],
        "result": result['message'],
        "status": result['status'],
    }), status_code
