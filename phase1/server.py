import EventMap
import Event
import EMController
import socket
import json
from threading import Thread

# Note: While allowing concurrent access to server, need to put lock
# on server and pass lock and condition variables to worker.
# Thesee might be implemented better if functions are converted to
# classes. For more info check 'Python notebook for 28th' 

def worker(sock):
	received = sock.recv(10)
	req = None
	if received and received != '':
		length = int(received)
		req = sock.recv(length)
        #req = sock.recv(1000)
	while req and req != '':
		req = req.rstrip()
		req_dict = json.loads(req.decode())
		if req_dict['ClassName'] == 'EventMap':
			process_EM(req_dict, sock)
		elif req_dict['ClassName'] == 'EMController':
			process_EMC(req_dict, sock)
		elif req_dict['ClassName'] == 'Event':
			process_E(req_dict, sock)
		else:
			try:
				raise NameError('ClassNameNotFound')
			except NameError:
				print('There is no Class with the given name!')
				raise
		sock.send(('request ' + req.decode() + ' processed').encode())
		received = sock.recv(10)
		req = None
		if received and received != '':
			length = int(received)
			req = sock.recv(length)
		#req = sock.recv(1000)
	print(sock.getpeername(), ' closing')

def process_EM(req_dict, sock):
	req_method = req_dict['Method']
	if req_method == '__init__':
		# Need to decide on how to handle Map Creations!
		# Utilizing EMController might be a better Idea
		pass
	elif req_method == 'insertEvent':
		_map_id = req_dict['Instance']
		evdict = req_dict['Args'][0]
		_lat = req_dict['Args'][1]
		_lon = req_dict['Args'][2]
		emc = EMController.EMController(_map_id)
		ev = Event.Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
		emc.eventmap.insertEvent(ev, _lat, _lon)
		# Note: emc.eventmap might not be the best practice
		# Might need a _getMapWithId(id) method
		# Note2: Not sure if it needs to do emc.save(name) here
		# I feel like user will call it explicitly via socket
		# Note3: Notification will go to observer
		# Might need to send something from the sock here!
	elif req_method == 'deleteEvent':
		_map_id = req_dict['Instance']
		_eid = req_dict['Args'][0]
		emc = EMController.EMController(_map_id)
		emc.eventmap.deleteEvent(_eid)
		# Same notes apply here!
	elif req_method == 'searchbyRect':
		_map_id = req_dict['Instance']
		_lattl = req_dict['Args'][0]
		_lontl = req_dict['Args'][1]
		_latbr = req_dict['Args'][2]
		_lonbr = req_dict['Args'][3]
		emc = EMController.EMController(_map_id)
		result = emc.eventmap.searchbyRect(_lattl, _lontl, _latbr, _lonbr)
		dump = json.dumps(result)
		sock.send(dump.encode())
		# Same notes apply here!
		# Note2: since event objects are dictionaries
		# I expect json to be able to dump them
	elif req_method == 'findClosest':
		_map_id = req_dict['Instance']
		_lat = req_dict['Args'][0]
		_lon = req_dict['Args'][1]
		emc = EMController.EMController(_map_id)
		result = emc.eventmap.findClosest(_lat, _lon)
		dump = json.dumps(result)
		sock.send(dump.encode())
		# Same notes apply here!
	elif req_method == 'searchbyTime':
		_map_id = req_dict['Instance']
		_stime = req_dict['Args'][0]
		_to = req_dict['Args'][1]
		emc = EMController.EMController(_map_id)
		result = emc.eventmap.searchbyTime(_stime, _to)
		dump = json.dumps(result)
		sock.send(dump.encode())
		# Same notes apply here!
	elif req_method == 'searchbyCategory':
		_map_id = req_dict['Instance']
		_catstr = req_dict['Args'][0]
		emc = EMController.EMController(_map_id)
		result = emc.eventmap.searchbyCategory(_catstr)
		dump = json.dumps(result)
		sock.send(dump.encode())
		# Same notes apply here!
	elif req_method == 'searchbyText':
		_map_id = req_dict['Instance']
		_catstr = req_dict['Args'][0]
		emc = EMController.EMController(_map_id)
		result = emc.eventmap.searchbyText(_catstr)
		dump = json.dumps(result)
		sock.send(dump.encode())
		# Same notes apply here!
	elif req_method == 'searchAdvanced':
		_map_id = req_dict['Instance']
		_rectangle = req_dict['Args'][0]
		_stime = req_dict['Args'][1]
		_to = req_dict['Args'][2]
		_category = req_dict['Args'][3]
		_text = req_dict['Args'][4]
		emc = EMController.EMController(_map_id)
		result = emc.eventmap.searchAdvanced(_rectangle, _stime, _to, _category, _text)
		dump = json.dumps(result)
		sock.send(dump.encode())
		# Same notes apply here!
	elif req_method == 'watchArea':
		_map_id = req_dict['Instance']
		_rectangle = req_dict['Args'][0]
		_callback = req_dict['Args'][1] # Decide what to do!
		_category = req_dict['Args'][2]
		emc = EMController.EMController(_map_id)
		emc.eventmap.watchArea(_rectangle, _callback, _category)
		# Same notes apply here!

def process_EMC(req_dict, sock):
	req_method = req_dict['Method']
	if req_method == '__init__':
		# Need to decide on what to do with new EMC Creations
		pass
	elif req_method == 'dettach':
		_map_id = req_method['Instance']
		emc = EMController.EMController(_map_id)
		emc.dettach()
	elif req_method == 'save':
		_map_id = req_method['Instance']
		_name = req_method['Args'][0]
		emc = EMController.EMController(_map_id)
		emc.save(_name)
	elif req_method == 'load':
		_name = req_method['Args'][0]
		_id = EMController.EMController.load(_name)
		# Should I return the id to caller?
		dump = json.dumps(_id)
		sock.send(dump.encode())
	elif req_method == 'list':
		# Map objects are not json serializable
		# Therefore I can return (id, name) pairs
		# Writing getters for id and name might be better
		result = EMController.EMController.list()
		pairs = []
		for _map in result:
			pairs.append((_map.id, _map.name))
		dump = json.dumps(pairs)
		sock.send(dump.encode())
	elif req_method == 'delete':			
		_name = req_method['Args'][0]
		EMController.EMController.delete(_name)
		# Do we need to send any sor of notification?
		# It feels so, but should it be done here?
		# Or something related with observers?

def server(port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('', port))
	s.listen(10)    # 10 is queue size for "not yet accept()'ed connections"
	try:
		while True:
			ns, peer = s.accept()
			print(peer, 'connected.')
			t = Thread(target = worker, args = (ns, ))
			t.start()
	finally:
		s.close()
