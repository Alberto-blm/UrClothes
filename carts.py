from flask import Blueprint, request, jsonify
from . import db
import json


bp = Blueprint('carts', __name__, url_prefix='/carts')

@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
def users_funct():
    user_id = request.args.get('id')
    skip = request.args.get('skip')
    limit = request.args.get('limit')

    request_body = request.get_json()
    if request.method == 'POST':
        # Crear carrera
        return jsonify({'_id': db.new_cart(request_body)})
    elif request.method == 'PUT':
    # Actualizar nombre y descripcion de la carrera
        return jsonify({'_id': db.update_user(request_body)})
    elif request.method == 'DELETE' and user_id is not None:
        # Borrar una carrera usando el _id
        return jsonify({'borrados': db.delete_user_id(user_id)})
    elif user_id is not None:
        # Obtener carreras por _id
        result = db.read_user_id(user_id)
        return jsonify({'user': json.loads(result)})
    else:
        # Obtener carreras
        skip = (skip, 0)[skip is None]
        limit = (limit, 10)[limit is None]
        result = db.read_carts(skip, limit)
        return jsonify({'carts': json.loads(result)})

@bp.route('/list', methods=['GET'])
def news():
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    limit = (limit, 20)[limit is None]
    # Crear carrera
    result = db.read_carts(limit)
    return jsonify({'cart': json.loads(result)})
