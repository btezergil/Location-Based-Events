import EventMap
import Event
import EMController
import socket
import json
import pickle
from threading import Thread

# Note: While allowing concurrent access to server, need to put lock
# on server and pass lock and condition variables to worker.
# These might be implemented better if functions are converted to
# classes. For more info check 'Python notebook for 28th' 

def worker(sock):
	received = sock.recv(10)
	req = None
	if received and received != '':
		length = int(received)
		req = sock.recv(length)
        #req = sock.recv(1000)
	emc = None
	events = []
	while req and req != '':
		req = req.rstrip()
		req_dict = json.loads(req.decode())
		if req_dict['ClassName'] == 'EMController':
			emc = process_EMC(req_dict, sock, emc, events)
		elif req_dict['ClassName'] == 'Event':
			process_E(req_dict, sock, events)
		else:
			try:
				raise NameError('ClassNameNotFound')
			except NameError:
				print('There is no Class with the given name!')
				pass
		#sock.send(('request ' + req.decode() + ' processed').encode())
		received = sock.recv(10)
		req = None
		if received and received != '':
			length = int(received)
			req = sock.recv(length)
		#req = sock.recv(1000)
	print(sock.getpeername(), ' closing')

def process_EMC(req_dict, sock, emc, events):
	METHOD_RETURN_EVENT = ["searchbyRect", "findClosest", "searchbyTime", "searchbyCategory", "searchbyText", "searchAdvanced"]
	req_method = req_dict['Method']
	if req_method == 'new':
		try:
			args = req_dict['Args']
			emc = EMController.EMController(*args)
			n_msg = "EMController with id = {} created.".format(getattr(emc, 'id'))
			#print(req_method,'called with args=', args)
			print(n_msg)
			sock.send(n_msg.encode())
		except Exception as e:
			e_msg = "ERROR creating new EMController"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method == 'load':
		try:
			args = req_dict['Args']
			EM_id = getattr(EMController.EMController, req_method)(*args)
			emc = EMController.EMController(EM_id)
			n_msg = "EMController with id = {} loaded.".format(EM_id)
			print(req_method,'called with args=', args)
			print(n_msg)
			sock.send(n_msg.encode())
		except Exception as e:
			e_msg = "ERROR executing EMC.load method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method == 'insertEvent':
		try:
			args = req_dict['Args']
			_eid = int(args[0])
			args = args[1:]
			ev = None
			for e in events:
				if getattr(e,'_id') == _eid:
					ev = e
					break;
			args.insert(0, ev)
			getattr(emc, req_method)(*args)
			n_msg = "{} operation is successful.".format(req_method)
			sock.send(n_msg.encode())
			print(req_method,'called with args=', args, 'on', emc)
		except Exception as e:
			e_msg = "ERROR executing insertEvent method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method == "deleteEvent":
		try:
			args = req_dict['Args']
			print("args=", args)
			result = getattr(emc, req_method)(*args)
			print(req_method,'called with args=', args, 'on', emc)
			for e in events:
				if getattr(e, '_id') == args[0]:
					events.remove(e)
			n_msg = "deleteEvent successful."
			sock.send(n_msg.encode())
		except Exception as e:
			e_msg = "ERROR executing deleteEvent method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method in METHOD_RETURN_EVENT:
		try:
			args = req_dict['Args']
			if req_method == "searchAdvanced":
				args[0] = json.loads(args[0])
				# trick to interpret as rectangle
			result = getattr(emc, req_method)(*args)
			result = ["Event id = {}, lat = {}, lon = {}".format(x._id,x.lat,x.lon) for x in result]
			dump = json.dumps(result)
			sock.send(dump.encode())
			print(req_method,'called with args=', args, 'on', emc)
		except Exception as e:
			e_msg = "ERROR executing Map method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method == "watchArea":
		try:
			args = req_dict['Args']
			args[0] = json.loads(args[0])
			# trick to interpret as rectangle
			# TODO: Create a new thread for observer
			pass
		except Exception as e:
			e_msg = "ERROR executing WatchArea method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method in ['list', 'delete']: # These are class methods
		try:
			args = req_dict['Args']
			result = getattr(EMController.EMController, req_method)(*args)
			if result is not None:
				dump = json.dumps(result)
				sock.send(dump.encode())
			else:
				n_msg = "{} operation on EMC with id = {} is successful".format(req_method, getattr(emc, 'id'))
				sock.send(n_msg.encode())
			print(req_method,'called with args=', args)
		except Exception as e:
			e_msg = "ERROR executing EMC class method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method in ['save', 'dettach']:
		try:
			args = req_dict['Args']
			result = getattr(emc, req_method)(*args)
			if result is not None:
				dump = json.dumps(result)
				sock.send(dump.encode())
			else:
				n_msg = "{} operation on EMC with id = {} is successful".format(req_method, getattr(emc, 'id'))
				sock.send(n_msg.encode())
			print(req_method,'called with args=', args, 'on', emc)
		except Exception as e:
			e_msg = "ERROR executing EMC method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	return emc

def process_E(req_dict, sock, events):
	METHOD_LIST = ["getEvent", "getMap"]
	req_method = req_dict['Method']
	if req_method == 'new': # Event Constructor
		try:
			args = req_dict['Args']
			ev = Event.Event(*args)
			events.append(ev)
			n_msg = "Event with id = {} created.".format(ev._id)
			#print(req_method,'called with args=', args)
			print(n_msg)
			sock.send(n_msg.encode())
		except Exception as e:
			e_msg = "ERROR creating new Event"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method == "updateEvent":
		try:
			args = req_dict['Args']
			args[0] = json.loads(args[0]) # Little trick to infer argument as dictionary	
			_eid = req_dict['Instance']
			for e in events:
				if e._id == _eid: #getattr(e,'_id')
					ev = e
					break;
			print(req_method,'called with args=', args, 'on', ev)
			getattr(ev, req_method)(*args)
			n_msg = "{} with Event id = {} is successful.".format(req_method, _eid)
			sock.send(n_msg.encode())
		except Exception as e:
			e_msg = "ERROR executing updateEvent method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method in METHOD_LIST:
		try:
			args = req_dict['Args']
			_eid = req_dict['Instance']
			for e in events:
				if e._id == _eid: #getattr(e,'_id')
					ev = e
					break;
			print(req_method,'called with args=', args, 'on', ev)
			result = getattr(ev, req_method)(*args)
			if req_method == "getMap":
				result = getattr(result, 'id')
			if result is not None:
				dump = json.dumps(result)
				sock.send(dump.encode())
			else:
				n_msg = "{} called successfully.".format(req_method)
		except Exception as e:
			e_msg = "ERROR executing Event method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	
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

serv = Thread(target = server, args=(20445,))
serv.start()
