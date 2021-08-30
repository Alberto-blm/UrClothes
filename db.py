from bson.json_util import dumps, loads, ObjectId
from bson.regex import str_flags_to_int
from flask import current_app
from flask.json import jsonify
from pymongo import MongoClient, DESCENDING
import pymongo
from werkzeug.local import LocalProxy
import hashlib
import json
from . import config as c
import jwt
import datetime
import numpy as np
import os
from sklearn import ensemble, svm, tree, neighbors
import pandas as pd

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


def get_role(token_id):
    return dumps(db.users.find_one({'_id': ObjectId(token_id['UserId'])}))


def read_user_update(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    user["_id"] = str(user["_id"])
    return dumps(user)


def read_users(skip, limit):
    return dumps(db.users.find({}).skip(int(skip)).limit(int(limit)))


def signIn(data):

    pwd = str(data["pwd"]).encode()
    hash_pwd = hashlib.sha512(pwd)
    mail = str(data["email"])
    user = db.users.find_one({'email': mail})
    if(user!= None):
        user["_id"] = str(user["_id"])
    if(user == None):
        return "User not found",422
    elif(user["pwd"] != hash_pwd.hexdigest()):
        return "Invalid password",401
    else:
        new_cart(user["_id"])
        token = jwt.encode({"UserId": user["_id"]}, c.SECRET_KEY, algorithm="HS256")
        tokenResponse = jsonify({'token': token})
        return tokenResponse,200


#------------------Clothes-----------

def read_cloth_id(cloth_id):
    data = dumps(db.clothes.find_one({'_id': ObjectId(cloth_id)}))
    return None


def read_clothes(skip, limit):
    return dumps(db.clothes.find({}).skip(int(skip)).limit(int(limit)))


def read_cloth_type(cloth_name):
    cloth = loads(dumps(db.clothes.find({'name': cloth_name['name']})))
    for i in cloth:
        i['_id'] = str(i['_id'])
    return dumps(cloth)


def search(data):
    cloth = loads(dumps(db.clothes.find({'category': {'$all': data['category']}})))
    for i in cloth:
        i['_id'] = str(i['_id'])
    return dumps(cloth)


def news(limit):
    cloth = loads(dumps(db.clothes.find({}).sort('_id', -1).limit(int(limit))))
    for i in cloth:
        i['_id'] = str(i['_id'])

    return dumps(cloth)


def add_cloth(data):
    cloth = loads(dumps(db.clothes.find({'name': data['name'], 'size': data['size']},)))
    if(cloth ==[]):
        return str(db.clothes.insert_one(data))
    else:
        return 


def update_cloth(data):
    cloth = loads(dumps(db.clothes.find({'name': data['name'], 'size': data['size']},)))
    print(data)
    if(cloth == []):
        return
    if(data['brand'] != ""):
        db.clothes.update_one({'name': data['name'], 'size': data['size']},{'$set':{'brand': data['brand']}})
    if(data['price'] != 0):
        db.clothes.update_one({'name': data['name'], 'size': data['size']},{'$set':{'price': data['price']}})
    if(data['stock'] != 0):
        db.clothes.update_one({'name': data['name'], 'size': data['size']},{'$set':{'stock': data['stock']}})
    return "Success"


def delete_cloth(data):
    cloth = loads(dumps(db.clothes.find({'name': data['name'], 'size': data['size']},)))
    if(cloth ==[]):
        return 
    else:
        return str(db.clothes.delete_one({'name': data['name'], 'size': data['size']}))


def get_categories():
    return dumps(db.categories.find({}))


#------------------Carts-----------

def new_cart(userId):
    newCart={
        'userId': userId,
        'price': 0,
        'items': []
    }
    cart = db.carts.find_one({'userId': userId})
    if(cart == None):
        return str(db.carts.insert_one(newCart))


def read_carts_list(limit, token_id):
    cloth = loads(dumps(db.buyed.find({'userId': token_id['UserId']}).sort('_id', -1).limit(int(limit))))
    return dumps(cloth)


def read_cart_id(user_id):
    return dumps(db.carts.find_one({'userId': user_id['UserId']}))


def add_to_cart(user_id, item):
    cart = loads(dumps(db.carts.find_one({'userId': user_id['UserId']})))
    cloth = loads(dumps(db.clothes.find_one({'_id': ObjectId(item['clothId'])})))
    print('llego al add')
    if( cart['items']!= []):
        print("entro al if grande")
        for i in cart['items']:
            print(i)
            if(i == item['clothId']):
                print(cart['items'].index(i))
                index = cart['items'].index(i)
                #Restauramos stock
                cloth['stock'] = cloth['stock'] + cart['units'][index]
                db.clothes.update_one({'_id': cloth['_id']},{'$set': {'stock': cloth['stock']}})
                #restamos el nuevo stock
                cloth['stock'] = cloth['stock'] - item['units']
                db.clothes.update_one({'_id': cloth['_id']},{'$set': {'stock': cloth['stock']}})
                #Restauramos precio
                cart['price'] = cart['price'] - (item['price']*cart['units'][index])
                db.carts.update_one({'userId': user_id['UserId']},{'$set': {'price': cart['price']}})
                #restamos el nuevo precio
                cart['price'] = cart['price'] + (item['price']*item['units'])
                db.carts.update_one({'userId': user_id['UserId']},{'$set': {'price': cart['price']}})
                #actualizamos unidades
                cart['units'][index] = item['units']
                return str(db.carts.update_one({'userId': user_id['UserId']},{'$set':{'units': cart['units']}}))
            
        print("entro al else")
        cloth['stock'] = cloth['stock'] - item['units']
        db.clothes.update_one({'_id': cloth['_id']},{'$set': {'stock': cloth['stock']}})
        cart['price'] = cart['price'] + (item['price']*item['units'])
        db.carts.update_one({'userId': user_id['UserId']},{'$set': {'price': cart['price']}})
        return str(db.carts.update_one({'userId': user_id['UserId']},{'$push':{'items': item['clothId'], 'units': item['units']}}))
    else:
        print("entro al else grande")
        cloth['stock'] = cloth['stock'] - item['units']
        db.clothes.update_one({'_id': cloth['_id']},{'$set': {'stock': cloth['stock']}})
        cart['price'] = cart['price'] + (item['price']*item['units'])
        db.carts.update_one({'userId': user_id['UserId']},{'$set': {'price': cart['price']}})
        return str(db.carts.update_one({'userId': user_id['UserId']},{'$push':{'items': item['clothId'], 'units': item['units']}}))
        

def delete_from_cart(user_id, item):
    cart = loads(dumps(db.carts.find_one({'userId': user_id['UserId']})))
    cloth = loads(dumps(db.clothes.find_one({'_id': ObjectId(item['clothId'])})))
    cloth['stock'] = cloth['stock'] + item['units']
    db.clothes.update_one({'_id': cloth['_id']},{'$set': {'stock': cloth['stock']}})
    cart['price'] = (cart['price']) - (item['price'] * cart['units'][item['index']])
    db.carts.update_one({'userId': user_id['UserId']},{'$set': {'price': cart['price']}})
    return str(db.carts.update_one({'userId': user_id['UserId']},{'$pull':{'items': item['clothId'], 'units': cart['units'][item['index']]} }))


def get_cart(user_id):
    cart = loads(dumps(db.carts.find_one({'userId': user_id['UserId']})))
    
    i=0
    while i < len(cart['items']):
        cart['items'][i] = ObjectId(cart['items'][i])
        i=i+1
   
    return dumps(db.clothes.find({'_id':{'$in': cart['items']}}))


def get_order(data):
    cart = loads(dumps(db.buyed.find_one({'_id': ObjectId(data['id'])})))
    print(cart['items'])
    i=0
    while i < len(cart['items']):
        cart['items'][i] = ObjectId(cart['items'][i])
        i=i+1
    
    return dumps(db.clothes.find({'_id':{'$in': cart['items']}}))


def pay_cart(user_id):
    cart = loads(dumps(db.carts.find_one({'userId': user_id['UserId']})))
    date = str(datetime.date.today())
    data ={
        'userId': cart['userId'],
        'price': cart['price'],
        'date': date,
        'items': cart['items']
    }
   
    db.buyed.insert_one(data)
    cart['price'] = 0
    cart['items'] = []

    return str(db.carts.update_one({'userId': cart['userId']},{'$set':{'price': cart['price'], 'items': cart['items']}}))


def get_cart_price(user_id):
    cart = loads(dumps(db.carts.find_one({'userId': user_id['UserId']})))
    
    price = cart['price']
    return dumps(price)
#------------------Others-----------

def get_units(user_id):
    
    return dumps(db.carts.find_one({'userId': user_id['UserId']}))