#!/usr/bin/python

import requests, json, xspf
import sys
import flask_api
from flask import request, g, jsonify, Response, make_response
from flask_api import FlaskAPI, status, exceptions
from pymemcache.client.base import Client



app = FlaskAPI(__name__)


def json_serializer(key, value):
	
	print("in ser",type(value))
	
	if type(value) == str:
		return value,1
		
	return json.dumps(value),2

def json_deserializer(key, value, flags):
	
	print("in deser",type(value))
	
	if flags == 1:
		return value.decode('utf-8')
		
	if flags == 2:
		return json.loads(value.decode('utf-8'))
		
	raise Exception("Unknown serialization format")

#connection to memcached 
def getMemcacheData():
	client = Client(('localhost', 11211), serializer=json_serializer,deserializer=json_deserializer)
	result = client.get('playlist_json')
	return result

def setMemcacheData(jsonObj):
	client = Client(('localhost', 11211), serializer=json_serializer,deserializer=json_deserializer)
	client.set('playlist_json',jsonObj ,expire=120)
	return "success"


def getXSPFXml(json_object):
	print("In getXSPFXml()",json_object)
	#json_object = json_object.replace("b\\"," ")
	if len(json_object) > 0:
		
		xmlObj = xspf.Xspf()
		print("1:",json_object[0])
		
		play_jsn = json_object[0]
		print("2:playlist_title:",play_jsn["playlist_title"])
		
		xmlObj.title = play_jsn["playlist_title"]
		xmlObj.creator = play_jsn["user_name"]
		
		for list1 in json_object:
			track_title = list1["track_title"]
			print("3:track_title:",track_title)
			track_url = 'http://localhost:8000/tracks/'+str(track_title)
			track_headers = {'content-type': 'application/xspf+xml'}
			track_res = requests.get(track_url,headers=track_headers)
			track_jsonObj = track_res.json()
			print("4:track_jsonObj:",track_jsonObj)
			if len(track_jsonObj) > 0:
				track_jsn = track_jsonObj[0]
				print("5:track json:::",track_jsn)
				#for trackList in track_jsonObj:
				trackTitle = track_jsn["track_title"]
				trackCreator = track_jsn["track_artist"]
				track_node = xspf.Track(title=trackTitle, creator=trackCreator,album=track_jsn["album_title"])
				track_node.trackNum = str(track_jsn["track_id"])
				track_node.location = track_jsn["media_url"]
				track_node.duration = str(track_jsn["track_length"])
				xmlObj.add_track(track_node)
	finalxml = xmlObj.toXml()	
	#finalxml = finalxml.replace("b'"," ")
	
	print("End getXSPFXml() final xspf xml:",finalxml)			
	return finalxml

# To get  playlists xspf xml by id
@app.route("/playlist/<playlist_title>",methods=['GET'])
def get_all_playlistbyid(playlist_title):
	try:
		result = getMemcacheData()
		if result is None:
			url = 'http://localhost:8000/playlistsbytitle/'+playlist_title
			headers = {'content-type': 'application/xspf+xml'}
			print("if result none play title:",playlist_title);
		
			playlist_res = requests.get(url,headers=headers)
			print("1:playlist playlist_res:",playlist_res)
		
			json_object = playlist_res.json()
			print("2:playlist json:",json_object)
			setMemcacheData(json_object) # stored for the next repetitive hit
			playlistXml = getXSPFXml(json_object)
		else:
			print("in else")
			playlistXml = getXSPFXml(result)	
		
		print(playlistXml[0])			
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOT_FOUND

	return Response(playlistXml, mimetype='text/xml') 






if __name__ == "__main__":
	app.run(debug=True,port=5200)
