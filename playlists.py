import sys
import flask_api
import datetime
from flask import request, g, jsonify, Response
from flask_api import FlaskAPI,status, exceptions
from cassandra.cluster import Cluster

app = FlaskAPI(__name__) 

@app.route('/', methods=['GET'])
def home():
    return "Playlists API"


@app.route("/playlists",methods=['POST'])
def create_playlists():
	mandatory_fields = ['playlist_title','user_name','track_title']

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()

	playlist_title = request.data.get('playlist_title','')
	user_name = request.data.get('user_name','')
	track_title = request.data.get('track_title','')
	description = request.data.get('description','')

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
	curDate = datetime.datetime.now()

	rows = session.execute("""Select id from musicData where track_title = %(track_title)s ALLOW FILTERING;""",{'track_title':track_title})

	id = None
	for row in rows:
		id = row.id

	if id is None:
		return 'track_title ID Not found'
	else:
		rows = session.execute("""Select user_name,playlist_title, album_title, track_artist, track_length, media_url, album_url from musicData where id = %(id)s ALLOW FILTERING;""",{'id':id})

		u_name = None
		p_title = None
		for row in rows:
			u_name = row.user_name
			p_title = row.playlist_title
			a_title = row.album_title
			t_artist = row.track_artist
			t_length = row.track_length
			m_url = row.media_url
			a_url = row.album_url

		if u_name is None:
			session.execute("""UPDATE musicData
			set playlist_title = %(playlist_title)s,
			user_name = %(user_name)s,
			description = %(description)s,
			modifieddate = %(modifieddate)s
			where Id = %(id)s""",
			{'playlist_title': playlist_title, 'user_name': user_name, 'description': description, 'id':id, 'modifieddate': str(curDate)})
		else:
			rows = session.execute("Select max(Id) as id from musicData")

			for row in rows:
					new_id = row.id

			if new_id is None:
				new_id = 1
			else:
				new_id = new_id + 1

			if(u_name == user_name):
				if(p_title == playlist_title):				
					return 'same user_name and same playlist already exists!!!'
				else:
					session.execute("""INSERT into musicData (track_title, album_title, track_artist, track_length, media_url, album_url, playlist_title, user_name, description, id, createddate) 
					values (%(track_title)s, %(album_title)s, %(track_artist)s, %(track_length)s, %(media_url)s, %(album_url)s, %(playlist_title)s,%(user_name)s,%(description)s, %(new_id)s, %(createddate)s)""",
					{'track_title': track_title, 'album_title': a_title, 'track_artist': t_artist, 'track_length':t_length, 'media_url':m_url, 'album_url':a_url, 'playlist_title': playlist_title, 'user_name': user_name, 'description': description,  'new_id':new_id, 'createddate': str(curDate)})
			else:
	
				session.execute("""INSERT into musicData (track_title, album_title, track_artist, track_length, media_url, album_url, playlist_title, user_name, description, id, createddate) 
				values (%(track_title)s, %(album_title)s, %(track_artist)s, %(track_length)s, %(media_url)s, %(album_url)s, %(playlist_title)s,%(user_name)s,%(description)s, %(new_id)s, %(createddate)s)""",
				{'track_title': track_title, 'album_title': a_title, 'track_artist': t_artist, 'track_length':t_length, 'media_url':m_url, 'album_url':a_url, 'playlist_title': playlist_title, 'user_name': user_name, 'description': description,  'new_id':new_id,'createddate': str(curDate)})


	response  = Response(status=201)
	response.headers['location'] = '/playlistsbyuser/'+user_name
	response.headers['status'] = '201 Created'

	return response, status.HTTP_201_CREATED


#To get particular plalist info
@app.route("/playlists/<playlist_id>",methods=['GET'])
def get_playlist(playlist_id):
	try:
		cluster = Cluster(['172.17.0.2'])
		session = cluster.connect('music')
		curDate = datetime.datetime.now()

		result = session.execute("""select user_name,playlist_title,track_id from musicData where playlist_id = %(playlist_id)s ALLOW FILTERING;""", {'playlist_id':playlist_id})
		
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOT_FOUND
        	
	if result is None:
		return { 'error': str(e) }, status.HTTP_404_NOT_FOUND
	
	return jsonify(list(result)), status.HTTP_200_OK


@app.route("/playlists",methods=['GET'])
def get_all_playlists():

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
	result = session.execute("select * from musicData")

	if result is None:
		resp = Response(status=404, mimetype='application/json')
		return resp

	return jsonify(list(result))


@app.route("/playlistsbytitle/<playlist_title>",methods=['GET'])
def get_playlistByTitle(playlist_title):

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')

	result = session.execute("select user_name,playlist_title,createddate,track_title from musicData where playlist_title ='%s' ALLOW FILTERING" %playlist_title)

	if result is None:
		resp = Response(status=404, mimetype='application/json')
		return resp

	return jsonify(list(result))


@app.route("/playlistsbyname/<user_name>",methods=['GET'])
def get_playlistByName(user_name):

	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')

	result = session.execute("select user_name,playlist_title,createddate from musicData where user_name ='%s' ALLOW FILTERING" %user_name)

	if result is None:
		resp = Response(status=404, mimetype='application/json')
		return resp

	return jsonify(list(result))

@app.route("/playlists/<playlist_title>",methods=['DELETE'])
def delete_playlist(playlist_title):
	
	cluster = Cluster(['172.17.0.2'])
	session = cluster.connect('music')
	rows = session.execute("""Select id from musicData where playlist_title = %(playlist_title)s ALLOW FILTERING;""",{'playlist_title':playlist_title})

	idNo = None
	for row in rows:
		idNo = row.id

	if idNo is None:
		return 'playlist_title ID Not found'

	session.execute("delete from musicData where Id = %(idNo)s",{'idNo':idNo})

	resp = Response(status=200, mimetype='application/json')
            
	return resp


if __name__ == "__main__":
	app.run(debug=True)
	
