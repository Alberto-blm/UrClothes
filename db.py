from bson.json_util import dumps, loads, ObjectId
from flask import current_app
from pymongo import MongoClient, DESCENDING
import pymongo
from werkzeug.local import LocalProxy
import hashlib
import json
from . import config as c

#Config BBDD



def get_db():
    client = MongoClient('mongodb+srv://'+c.DB_USER+':'+c.DB_PASSWORD+'@urclothes.wlrcx.mongodb.net/')
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
    if(user['pwd'] == None):
        return str(db.users.update_one({'_id': ObjectId(user['_id'])},{'$set':{'name': user['name'],'surname': user['surname'],'email': user['email'],'address': user['address']}}))
    else:
        pwd = str(user["pwd"]).encode()
        hash_pwd = hashlib.sha512(pwd)
        return str(db.users.update_one({'_id': ObjectId(user['_id'])},{'$set':{'name': user['name'],'surname': user['surname'],'email': user['email'],'address': user['address'],'pwd': hash_pwd.hexdigest()}}))


def delete_user_id(user_id):
    return str(db.users.delete_one({'_id': ObjectId(user_id)}))


def read_user_id(user_id):
    return dumps(db.users.find_one({'_id': ObjectId(user_id)}))


def read_users(skip, limit):
    return dumps(db.users.find({}).skip(int(skip)).limit(int(limit)))

def signIn(data):
    pwd = str(data["pwd"]).encode()
    hash_pwd = hashlib.sha512(pwd)
    mail = str(data["email"])
    user = db.users.find_one({'email': mail})
    user["_id"] = str(user["_id"])
    if(user == None):
        return ''
    elif(user["pwd"] != hash_pwd.hexdigest()):
        return ''
    else:
        return dumps(user)


#------------------Clothes-----------

def read_cloth_id(cloth_id):
    data = dumps(db.clothes.find_one({'_id': ObjectId(cloth_id)}))
    print(data)
    return None

def read_clothes(skip, limit):
    return dumps(db.clothes.find({}).skip(int(skip)).limit(int(limit)))

def read_cloth_type(cloth_type):
    return dumps(db.clothes.find({'brand': cloth_type}))

def news(limit):
    cloth = loads(dumps(db.clothes.find({}).sort('_id', -1).limit(int(limit))))
    for i in cloth:
        i['_id'] = str(i['_id'])

    return dumps(cloth)

#------------------Carts-----------

def new_cart(data):
    return str(db.carts.insert_one(data))


def read_carts(limit):
    cloth = loads(dumps(db.carts.find({}).sort('_id', -1).limit(int(limit))))
    return dumps(cloth)

