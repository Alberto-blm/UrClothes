from flask import Blueprint, request, jsonify
from . import db
import json


bp = Blueprint('clothes', __name__, url_prefix='/clothes')

@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
def users_funct():
    cloth_id = request.args.get('id')
    cloth_type = request.args.get('brand')
    skip = request.args.get('skip')
    limit = request.args.get('limit')

    request_body = request.get_json()
    if request.method == 'POST':
        # Crear carrera
        return jsonify({'_id': db.create_user(request_body)})
    elif request.method == 'PUT':
    # Actualizar nombre y descripcion de la carrera
        return jsonify({'modificados': db.update_user(request_body)})
    elif request.method == 'DELETE' and cloth_id is not None:
        # Borrar una carrera usando el _id
        return jsonify({'borrados': db.delete_user_id(cloth_id)})
    elif cloth_id is not None:
        # Obtener ropa por _id
        result = db.read_cloth_id(cloth_id)
        return jsonify({'cloth': json.loads(result)})
    elif cloth_type is not None:
        result = db.read_cloth_type(cloth_type)
        return jsonify({'cloth': json.loads(result)})
    else:
        # Novedades
        skip = (skip, 0)[skip is None]
        limit = (limit, 10)[limit is None]
        result = db.read_clothes(skip, limit)
        return jsonify({'cloth': json.loads(result)})

@bp.route('/news', methods=['GET'])
def news():
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    limit = (limit, 20)[limit is None]
    # Crear carrera
    result = db.news(limit)
    return jsonify({'cloth': json.loads(result)})