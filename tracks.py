import sys
import flask_api
import datetime
from flask import request, g, jsonify, Response
from flask_api import FlaskAPI,status, exceptions
from cassandra.cluster import Cluster

app = FlaskAPI(__name__) 



@app.route('/', methods=['GET'])
def home():
    return "Tracks API"

@app.route("/tracks",methods=['POST'])
def create_tracks():
	mandatory_fields = ['track_title','album_title','track_artist','track_length','media_url']

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()

	track_title 	= request.data.get('track_title','')
	album_title 	= request.data.get('album_title','')
	artist 		= request.data.get('track_artist','')
	track_length 	= request.data.get('track_length','')
	media_url 	= request.data.get('media_url','')
	album_url 	= request.data.get('album_url','')

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
	curDate = datetime.datetime.now()
	
	rows = session.execute("Select max(Id) as id from musicData")

	for row in rows:
		id = row.id

	print("id:",id)
	if id is None:
		id = 1
	else:
		id = id + 1
	
	session.execute("""insert into musicData (track_id,track_title, album_title, track_artist, track_length, media_url, album_url, Id, createddate) 
	values (%(track_id)s,%(track_title)s, %(album_title)s, %(artist)s, %(track_length)s, %(media_url)s, %(album_url)s, %(id)s, %(createddate)s)""",
	{'track_id':str(id),'track_title': track_title, 'album_title': album_title, 'artist': artist, 'track_length': track_length, 'media_url': media_url, 'album_url': album_url,'id':id, 'createddate': str(curDate)})


	response  = Response('Track created successfully', mimetype='application/json')
	response.headers['location'] = '/tracksbyid/'+str(id)
	response.headers['status'] = '201 Created'
	
	return response, status.HTTP_201_CREATED



#To get all tracks info
@app.route("/tracks",methods=['GET'])
def get_all_tracks():

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
	result = session.execute("select track_id,track_title, album_title, track_artist, track_length, media_url, album_url, createddate from musicData")

	if result is None:
		resp = Response(status=404, mimetype='application/json')
		return resp

	return jsonify(list(result))


@app.route("/tracks/<title>",methods=['GET'])
def get_track(title):

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')

	result = session.execute("select track_id,track_title, album_title, track_artist, track_length, media_url, album_url from musicData where track_title ='%s' ALLOW FILTERING" %title)

	if result is None:
		resp = Response(status=404, mimetype='application/json')
		return resp

	return jsonify(list(result))


@app.route('/tracks', methods=['PUT'])
def update_article():

	rupdate_param =()
	mandatory_fields = ['track_title']

	if not all([field in request.data for field in mandatory_fields]):
		raise exceptions.ParseError()
	
	track_title 	= request.data.get('track_title')
	ntrack_title 	= request.data.get('new_track_title')
	nalbum_title 	= request.data.get('new_album_title','')


	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')

	curDate = datetime.datetime.now()

	rows = session.execute("""Select id from musicData where track_title = %(track_title)s ALLOW FILTERING;""",{'track_title':track_title})

	id = None
	for row in rows:
		id = row.id

	if id is None:
		return 'track_title ID Not found'

	session.execute("""UPDATE musicData
	    set track_title = %(ntrack_title)s,
	    album_title = %(nalbum_title)s
	    where Id = %(id)s""",
	     {'ntrack_title': ntrack_title, 'nalbum_title': nalbum_title,'id':id})

	resp = Response(status=200, mimetype='application/json')
	return resp


@app.route("/tracks/<track_title>",methods=['DELETE'])
def delete_tracks(track_title):
	
	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
	rows = session.execute("""Select id from musicData where track_title = %(track_title)s ALLOW FILTERING;""",{'track_title':track_title})

	idNo = None
	for row in rows:
		idNo = row.id

	if idNo is None:
		return 'track_title ID Not found'

	session.execute("delete from musicData where Id = %(idNo)s",{'idNo':idNo})

	resp = Response(status=200, mimetype='application/json')
            
	return resp

#To get particular plalist info
@app.route("/tracksbyid/<track_id>",methods=['GET'])
def get_playlist(track_id):
	
		cluster = Cluster(['172.17.0.2'])
		session = cluster.connect('music')
		#curDate = datetime.datetime.now()
		#print("track by id")
		result = session.execute("select track_id,track_title,album_title,track_artist,track_length,media_url,album_url from musicData where track_id = '%s' ALLOW FILTERING" %track_id)
		
		if result is None:
			resp = Response(status=404, mimetype='application/json')
			return "no data found"

		return jsonify(list(result))

if __name__ == "__main__":
	app.run(debug=True)
	
