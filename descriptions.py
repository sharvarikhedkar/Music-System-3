import sys
import flask_api
import datetime
from flask import request, g, jsonify, Response
from flask_api import FlaskAPI,status, exceptions
from cassandra.cluster import Cluster

app = FlaskAPI(__name__) 


@app.route('/', methods=['GET'])
def home():
    return "Descriptions API"

@app.route("/descriptions",methods=['POST'])
def create_trackdesc():
	mandatory_fields = ['track_description','user_name','track_title']

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()

	track_description = request.data.get('track_description','')
	user_name = request.data.get('user_name','')
	track_title = request.data.get('track_title','')

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
	curDate = datetime.datetime.now()

	rows = session.execute("""Select id from musicData where track_title = %(track_title)s and user_name = %(user_name)s ALLOW FILTERING;""",{'track_title':track_title, 'user_name':user_name})

	id = None
	for row in rows:
		id = row.id

	if id is None:
		return 'track_title ID Not found'
	else:
		session.execute("""UPDATE musicData
		set description = %(track_description)s,
		modifieddate = %(modifieddate)s
		where Id = %(id)s""",
		{'track_description': track_description, 'id':id, 'modifieddate': str(curDate)})


	resp = Response(status=201, mimetype='application/json')
	#resp.headers['location'] = 'http://localhost/article/search/' + title

	return resp


@app.route("/descriptions/<track>/<user_name>",methods=['GET'])
def get_descbyuser(track,user_name):

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')

	result = session.execute("select track_title, user_name,description ,createddate from musicData where track_title = %(track_title)s and user_name = %(user_name)s ALLOW FILTERING", {'track_title':track, 'user_name':user_name})

	if result is None:
		resp = Response(status=404, mimetype='application/json')
		return resp

	return jsonify(list(result))


if __name__ == "__main__":
	app.run(debug=True)
	