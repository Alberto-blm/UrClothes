from mmap import ACCESS_DEFAULT
from flask import Blueprint, request, jsonify
from . import db
import json
import jwt
from . import config
from functools import wraps

bp = Blueprint('clothes', __name__, url_prefix='/clothes')

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
        print(data)
        current_user = db.read_user_id(data['UserId'])
        print(current_user)
        if not current_user:
            return 'Unauthorized Access!', 401
        
        return f(*args, **kwargs)

    return decorated

@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
def users_funct():
    cloth_id = request.args.get('id')
    cloth_type = request.args.get('name')
    skip = request.args.get('skip')
    limit = request.args.get('limit')

    request_body = request.get_json()
    if request.method == 'POST':
        return jsonify({'_id': db.add_cloth(request_body)})
    elif request.method == 'PUT':
        return jsonify({'modificados': db.update_user(request_body)})
    elif request.method == 'DELETE' and cloth_id is not None:
        return jsonify({'borrados': db.delete_user_id(cloth_id)})
    elif cloth_id is not None:
        result = db.read_cloth_id(cloth_id)
        return jsonify({'cloth': json.loads(result)})
    elif cloth_type is not None:
        result = db.read_cloth_type(cloth_type)
        return jsonify({'cloth': json.loads(result)})
    else:
        skip = (skip, 0)[skip is None]
        limit = (limit, 10)[limit is None]
        result = db.read_clothes(skip, limit)
        return jsonify({'cloth': json.loads(result)})

@bp.route('/news', methods=['GET'])
def news():
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    limit = (limit, 10)[limit is None]
    result = db.news(limit)
    return jsonify({'cloth': json.loads(result)})


@bp.route('/search', methods=['POST'])
def search():
    request_body = request.get_json()
    result = db.search(request_body)
    return jsonify({'cloth': json.loads(result)})


@bp.route('/byName', methods=['POST'])
def get_by_name():
    request_body = request.get_json()
    
    result = db.read_cloth_type(request_body)
    return jsonify({'cloth': json.loads(result)})


@bp.route('/getCategories', methods=['GET'])
def categories():
    result = db.get_categories()
    return jsonify({'categories': json.loads(result)})


@bp.route('/updateCloth', methods=['POST'])
def update_cloth():
    request_body = request.get_json()
    result = db.update_cloth(request_body)
    return jsonify({'_id': result})


@bp.route('/deleteCloth', methods=['POST'])
def delete_cloth():
    request_body = request.get_json()
    result = db.delete_cloth(request_body)
    return jsonify({'_id': result})