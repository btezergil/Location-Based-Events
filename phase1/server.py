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
			emc = process_EMC(req_dict, sock, emc)
		elif req_dict['ClassName'] == 'Event':
			process_E(req_dict, sock, events)
		else:
			try:
				raise NameError('ClassNameNotFound')
			except NameError:
				print('There is no Class with the given name!')
				pass
		sock.send(('request ' + req.decode() + ' processed').encode())
		received = sock.recv(10)
		req = None
		if received and received != '':
			length = int(received)
			req = sock.recv(length)
		#req = sock.recv(1000)
	print(sock.getpeername(), ' closing')

def process_EMC(req_dict, sock, emc):
	METHOD_LIST_MAP = ["insertEvent", "deleteEvent", "searchbyRect", "findClosest", "searchbyTime", "searchbyCategory", "searchbyText", "searchAdvanced", "watchArea"]
	req_method = req_dict['Method']
	if req_method == 'new':
		try:
			args = req_dict['Args']
			emc = EMController.EMController(*args)
			n_msg = "EMController created"
			print(n_msg)
			sock.send(n_msg.encode())
		except Exception as e:
			e_msg = "ERROR creating new EMController"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method == 'load':
		try:
			args = req_dict['Args']
			emc = getattr(EMController.EMController, req_method)(*args)
			print(req_method,'called with args=', args)
		except Exception as e:
			e_msg = "ERROR executing EMC.load method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method in METHOD_LIST_MAP:
		try:
			args = req_dict['Args']
			result = getattr(emc, req_method)(*args)
			if result is not None:
				dump = json.dumps(result)
				sock.send(dump.encode())
			print(req_method,'called with args=', args, 'on', emc)
		except Exception as e:
			e_msg = "ERROR executing Map method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method in ['list', 'delete']: # These are class methods
		try:
			args = req_dict['Args']
			result = getattr(EMController.EMController, req_method)(*args)
			if result is not None:
				dump = json.dumps(result)
				sock.send(dump.encode())
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
			print(req_method,'called with args=', args, 'on', emc)
		except Exception as e:
			e_msg = "ERROR executing EMC method"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	return emc

def process_E(req_dict, sock, events):
	METHOD_LIST = ["updateEvent", "getEvent", "getMap"]
	req_method = req_dict['Method']
	if req_method == 'new': # Event Constructor
		try:
			args = req_dict['Args']
			ev = Event.Event(*args)
			events.append(ev)
			n_msg = "Event created"
			print("Event created", ev.getEvent())
			sock.send(n_msg.encode())
		except Exception as e:
			e_msg = "ERROR creating new Event"
			sock.send(e_msg.encode())
			print(e_msg, ":", e)
	elif req_method in METHOD_LIST:
		try:
			args = req_dict['Args']
			_eid = req_dict['Instance']
			for e in events:
				if getattr(e,_id) == _eid:
					ev = e
					break;
			result = getattr(ev, req_method)(*args)
			if result is not None:
				dump = json.dumps(result)
				sock.send(dump.encode())
			print(req_method,'called with args=', args, 'on', ev)
		except Exception as e:
			e_msg = "ERROR executing Event method "
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
