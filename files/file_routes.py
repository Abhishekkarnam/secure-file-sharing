from flask import Blueprint, request, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from files.file_service import save_secure_file, get_secure_file # Import both now
import io

file_bp = Blueprint('files', __name__)

@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    username = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify({"msg": "No file"}), 400
    
    file = request.files['file']
    result = save_secure_file(file, username)
    return jsonify(result), 200

@file_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download(filename):
    decrypted_data = get_secure_file(filename)
    if decrypted_data is None:
        return jsonify({"msg": "File not found"}), 404

    # Send the decrypted bytes back to the browser
    return send_file(
        io.BytesIO(decrypted_data),
        download_name=filename,
        as_attachment=True
    )

@file_bp.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    from database.models import FileMetadata
    files = FileMetadata.query.all()
    return jsonify([{"filename": f.filename, "owner": f.owner_id, "date": f.upload_date} for f in files])
