from bson.json_util import dumps, ObjectId
from flask import current_app
from pymongo import MongoClient, DESCENDING
from werkzeug.local import LocalProxy
import hashlib
import json

#Config BBDD
DB_USER = "admin"
DB_PWD = "altair98"
def get_db():
    client = MongoClient('mongodb+srv://'+DB_USER+':'+DB_PWD+'@urclothes.wlrcx.mongodb.net/')
    return client.UrClothes


db = LocalProxy(get_db)

def test_connection():
    return dumps(db.collection_names())


def collection_stats(collection_nombre):
    return dumps(db.command('collstats', collection_nombre))

#------------------usuarios-----------

def create_user(data):
    pwd = str(data["pwd"]).encode()
    hash_pwd = hashlib.sha512(pwd)
    data["pwd"] = hash_pwd.hexdigest()
    return str(db.users.insert_one(data))


def update_user(user):
    return str(db.users.update_one({'_id': ObjectId(user['_id'])},{'$set':{'email': user['email']}}))


def delete_user_id(user_id):
    return str(db.users.delete_one({'_id': ObjectId(user_id)}))


def read_user_id(user_id):
    return dumps(db.users.find_one({'_id': ObjectId(user_id)}))


def read_users(skip, limit):
    return dumps(db.users.find({}).skip(int(skip)).limit(int(limit)))

