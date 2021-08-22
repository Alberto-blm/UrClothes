from flask import Blueprint, request, jsonify
from . import db
import json
import jwt
from . import config
from functools import wraps 

bp = Blueprint('users', __name__, url_prefix='/users')
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
        #print(data)
        current_user = db.read_user_id(data['UserId'])
        #print(current_user)
        if not current_user:
            return 'Unauthorized Access!', 401
        
        return f(*args, **kwargs)

    return decorated


@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
def users_funct():
    #token = request.headers['x-access-token']
    #token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    user_id = request.args.get('id')
    skip = request.args.get('skip')
    limit = request.args.get('limit')

    request_body = request.get_json()
    if request.method == 'POST':
        # Crear carrera
        return jsonify({'_id': db.create_user(request_body)})
    elif request.method == 'PUT':
    # Actualizar nombre y descripcion de la carrera
        print(request_body)
        return jsonify({'_id': db.update_user(request_body)})
    elif request.method == 'DELETE' and user_id is not None:
        # Borrar una carrera usando el _id
        return jsonify({'borrados': db.delete_user_id(user_id)})
    elif user_id is not None:
        # Obtener carreras por _id
        
        result = db.read_user_id(user_id)
        return jsonify({'User': json.loads(result)})
    



@bp.route('/signIn', methods=['POST'])
def signIn_user():
    request_body = request.get_json()
    if request.method == 'POST':
        # Crear carrera
        return db.signIn(request_body)


@bp.route('/update', methods=['GET'])
@token_required
def update_user():

    token = request.headers['x-access-token']
    token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    

    if request.method == 'GET':
        # Crear carrera
        result = db.read_user_update(token_id['UserId'])
        
        return jsonify({'User': json.loads(result)})


@bp.route('/auth', methods=['POST'])
@token_required
def get_role():
    token = request.headers['x-access-token']
    token_id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    result = db.get_role(token_id)
    return result