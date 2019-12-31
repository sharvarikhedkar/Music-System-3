import sys
import flask_api
from flask import request, g, jsonify, Response
from flask_api import FlaskAPI, status, exceptions
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

from cassandra.cluster import Cluster

app = FlaskAPI(__name__) 

@app.route('/', methods=['GET'])
def home():
    return "Users API"


@app.route("/users",methods=['POST'])
def create_users():
	mandatory_fields = ['user_name','password','display_name','email_id']

	if not all([field in request.data for field in mandatory_fields]):
		raise exceptions.ParseError()
	
	user_name 	= request.data.get('user_name','')
	password 	= request.data.get('password','')
	hashed_password = generate_password_hash(password)
	display_name 	= request.data.get('display_name','')
	email_id 	= request.data.get('email_id','')
	home_url 	= request.data.get('home_url','')
	
	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')

	curDate = datetime.datetime.now()	

	session.execute("insert into users (user_name,hashed_password,display_name,email_id,home_url, createdDate, modifiedDate) values (%s, %s, %s, %s, %s, %s,%s)",(user_name, hashed_password, display_name, email_id, home_url, str(curDate), str(curDate)))


	#resp = Response(status=201, mimetype='application/json')
	response  = Response('User created successfully', mimetype='application/json')
	response.headers['location'] = '/users/'+str(user_name)
	response.headers['status'] = '201 Created'
	
	return response, status.HTTP_201_CREATED


@app.route("/users",methods=['GET'])
def get_users():
	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
	result = session.execute("select user_name,display_name,email_id,home_url,createdDate from users")
	print((result))
	
	"""if not result:
		return { 'message': "User not found" }, status.HTTP_404_NOT_FOUND
	else:
		return jsonify(list(result)), status.HTTP_200_OK"""

	return jsonify(list(result)), status.HTTP_200_OK


@app.route("/users/<user_name>",methods=['GET'])
def get_user(user_name):
	
	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
	result = session.execute("select user_name,display_name,email_id,home_url,createdDate from users where user_name ='%s'" %user_name)

	if result is None:
		resp = Response(status=404, mimetype='application/json')
		return resp

	return jsonify(list(result))



@app.route("/users/<user_name>",methods=['DELETE'])
def delete_users(user_name):

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')

	session.execute("delete from users where user_name = '%s'" %user_name)

	resp = Response(status=200, mimetype='application/json')
            
	return resp


@app.route("/users",methods=['PUT'])
def update_password():
	
	mandatory_fields = ["user_name","password","new_password"]

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()	

	user_name 	= request.data.get('user_name','')
	password 	= request.data.get('password','')
	new_password 	= request.data.get('new_password','')
	#date 		= str(datetime.datetime.now())

	new_hashed_password = generate_password_hash(new_password)
	
	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
            
	session.execute("update users set hashed_password = %(newpassword)s, modifieddate =%(date)s where user_name= %(user_name)s", {'user_name': user_name , "newpassword" : str(new_hashed_password), "date":str(datetime.datetime.now())})

	resp = Response(status=200, mimetype='application/json')

	return resp




if __name__ == "__main__":
	app.run(debug=True)
	
