from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, jwt_required

from database.models import SystemLog

log_bp = Blueprint('logs', __name__)


@log_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_logs():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Access Denied: Admin Only"}), 403

    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).all()
    return jsonify([
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "timestamp": log.timestamp.isoformat(),
            "status": log.status,
        }
        for log in logs
    ]), 200
