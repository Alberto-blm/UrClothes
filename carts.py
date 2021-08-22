from flask import Blueprint, request, jsonify
from . import db
import json
import jwt
from . import config
from functools import wraps

bp = Blueprint('carts', __name__, url_prefix='/carts')
current_user = None
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            print("ERROR NO ENCUENTRO EL TOKEN")
            return 'Unauthorized Access!', 401
        
        
        data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        current_user = db.read_user_id(data['UserId'])

        if not current_user:
            return 'Unauthorized Access!', 401
        
        return f(*args, **kwargs)

    return decorated

@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
def carts_funct():
    token = request.headers['x-access-token']
    token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
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
    elif token is not None:
        # Obtener carreras por _id

        result = db.read_cart_id(token_id)
        return jsonify({'Cart': json.loads(result)})
    

@bp.route('/list', methods=['GET'])
@token_required
def get_list():
    token = request.headers['x-access-token']
    token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    limit = (limit, 20)[limit is None]
    
    # Crear carrera
    result = db.read_carts_list(limit, token_id)
    return jsonify({'cart': json.loads(result)})


@bp.route('/add', methods=['POST'])
@token_required
def add_cloth():
    token = request.headers['x-access-token']
    token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    request_body = request.get_json()
    result = db.add_to_cart(token_id, request_body)
    return jsonify({'Cart': result})


@bp.route('/delete', methods=['POST'])
@token_required
def delete_coth():
    token = request.headers['x-access-token']
    token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    request_body = request.get_json()
    result = db.delete_from_cart(token_id, request_body)
    return jsonify({'Cart': result})


@bp.route('/cartItems', methods=['POST'])
@token_required
def get_cart():
    token = request.headers['x-access-token']
    token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    result = db.get_cart(token_id)
    return jsonify({'cart': json.loads(result)})


@bp.route('/orderItems', methods=['POST'])
@token_required
def order():
    token = request.headers['x-access-token']
    token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    request_body = request.get_json()
    result = db.get_order(request_body)
    return jsonify({'cart': json.loads(result)})


@bp.route('/pay', methods=['POST'])
@token_required
def pay():
    token = request.headers['x-access-token']
    token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])

    result = db.pay_cart(token_id)
    return jsonify({'cart': result})