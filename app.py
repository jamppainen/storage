from __future__ import print_function
import sys
import random
import uuid
import os
import boto3
import jwt

from botocore.exceptions import ClientError
from chalice import Chalice, AuthResponse, UnauthorizedError, NotFoundError, BadRequestError, Response
from chalicelib import auth, db

app = Chalice(app_name='storage')
app.debug = True

_DB = None
_USER_DB = None
_UNAVAILABLE=Response(body='Service Unavailable', status_code=503, headers={'Content-Type': 'text/plain'})

@app.authorizer(ttl_seconds=30)
def jwt_auth(auth_request):
    token = auth_request.token
    decoded = auth.decode_jwt_token(token)
    return AuthResponse(routes=['*'], principal_id=decoded['sub'])

@app.route('/v1/login', methods=['POST'])
def login():
    body = app.current_request.json_body
    try:
    	record = get_users_db().get_item(
        	Key={'username': body['username']})['Item']
    	jwt_token = auth.get_jwt_token(
        	body['username'], body['password'], record)
    except KeyError as e:
    	raise UnauthorizedError("Bad credentials")
    return {'token': jwt_token}

@app.route('/')
def index():
    return {'hello': 'world'}

@app.route('/v1/storage', methods=['POST'], authorizer=jwt_auth, content_types=['application/json'])
def create_storage():
	if generate_random_error():
		return _UNAVAILABLE
	username = get_authorized_username(app.current_request)
	data = None
	print(app.current_request.to_dict())
	if hasattr(app.current_request, 'json_body'):
		body = app.current_request.json_body
		if body != None:
			#print(body)
			try:
				data = body['data']
			except KeyError as e:
				raise BadRequestError("Unknown key, expected %s, found %s" % (e, body.keys()))
			except TypeError as e:
				raise BadRequestError(e)
	id = get_app_db().add_item(
		username=username,
		data=data)
	return {'id': id, 'data': data}

@app.route('/v1/storage/{id}', methods=['PUT'], authorizer=jwt_auth, content_types=['application/json'])
def update_storage(id):
	if generate_random_error():
		return _UNAVAILABLE
	username = get_authorized_username(app.current_request)
	body = app.current_request.json_body
	try:
		get_app_db().update_item(id, data=body['data'], username=username)
	except KeyError as e:
		raise BadRequestError("Unknown parameter, expected %s" % e)
	except TypeError as e:
		raise BadRequestError(e)
	return {'id': id, 'data':body['data']}

@app.route('/v1/storage/{id}', methods=['GET'], authorizer=jwt_auth)
def get_storage(id):
	if generate_random_error():	
		return _UNAVAILABLE
	username = get_authorized_username(app.current_request)
	storage = get_app_db().get_item(id, username=username)
	if storage == None:
		raise NotFoundError("Resource not found")
	return {'id': storage['uid'], 'data': storage['data']}

@app.route('/v1/storage/{id}', methods=['DELETE'], authorizer=jwt_auth)
def delete_storage(id):
	if generate_random_error():
		return _UNAVAILABLE
	username = get_authorized_username(app.current_request)
	try:
		get_app_db().delete_item(id, username=username)
	except ClientError as e:
		response_code = e.response['Error']['Code']
		if response_code == "ConditionalCheckFailedException":
			raise NotFoundError('Unknown identifier {}'.format(id))
	return 'OK'

def generate_random_error():
 	if random.randint(0,2) == 0:
 		return True
 	return False

def get_app_db():
    global _DB
    if _DB is None:
        _DB = db.StorageDB(
        	boto3.resource('dynamodb').Table(
                os.environ['APP_TABLE_NAME'])
        	)
    return _DB
	
def get_users_db():
    global _USER_DB
    if _USER_DB is None:
        _USER_DB = boto3.resource('dynamodb').Table(
            os.environ['USERS_TABLE_NAME'])
    return _USER_DB

def get_authorized_username(current_request):
    return current_request.context['authorizer']['principalId']

def get_hash(payload, salt=None):
    if salt is None:
        salt = os.urandom(16)
    rounds = 100000
    return hashlib.pbkdf2_hmac('sha256', payload, salt, rounds)
