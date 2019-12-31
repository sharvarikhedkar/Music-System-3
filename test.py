
import json
from pymemcache.client.base import Client

def json_serializer(key, value):
	
	print("in ser",type(value))
	
	if type(value) == str:
		return value,1
		
	return json.dumps(value),

def json_deserializer(key, value, flags):
	
	print("in deser",type(value))
	
	if flags == 1:
		return value.decode('utf-8')
		
	if flags == 2:
		return json.loads(value.decode('utf-8'))
		
	raise Exception("Unknown serialization format")

#client = Client(('localhost', 11211),serializer=json_serializer,deserializer=json_deserializer)
client = Client(('localhost', 11211),serializer=json_serializer,deserializer=json_deserializer)
#client.set_many(dict([('key_1',"test"),('key_2',"test2")]),expire=15)
result = client.get('playlist_json')
print(result)
#b = b'1234'
#print(b.decode('utf-8')) 

