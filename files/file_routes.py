from flask import Blueprint, request, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from files.file_service import save_secure_file, get_secure_file
from logs.logger import log_event
import io

file_bp = Blueprint('files', __name__)

@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    username = get_jwt_identity()
    if 'file' not in request.files:
        log_event(username, 'File Upload', 'FAILED')
        return jsonify({"msg": "No file"}), 400
    
    file = request.files['file']
    result = save_secure_file(file, username)
    status = 'SUCCESS' if result.get('filename') else 'FAILED'
    log_event(username, f"File Upload: {file.filename}", status)
    return jsonify(result), 200 if status == 'SUCCESS' else 400

@file_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download(filename):
    username = get_jwt_identity()
    decrypted_data = get_secure_file(filename)
    if decrypted_data is None:
        log_event(username, f"File Download: {filename}", 'FAILED')
        return jsonify({"msg": "File not found"}), 404

    log_event(username, f"File Download: {filename}", 'SUCCESS')
    return send_file(
        io.BytesIO(decrypted_data),
        download_name=filename,
        as_attachment=True
    )

@file_bp.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    from database.models import FileMetadata
    username = get_jwt_identity()
    files = FileMetadata.query.all()
    log_event(username, 'File List Viewed', 'SUCCESS')
    return jsonify([{"filename": f.filename, "owner": f.owner_id, "date": f.upload_date} for f in files])
