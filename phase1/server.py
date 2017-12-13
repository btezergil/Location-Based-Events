import EventMap
import Event
import EMController
import socket
import json
import pickle
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
		if req_dict['ClassName'] == 'EMController':
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

def process_EMC(req_dict, sock):
	METHOD_LIST = ["insertEvent", "deleteEvent", "searchbyRect", "findClosest", "searchbyTime", "searchbyCategory", "searchbyText", "searchAdvanced", "watchArea", "dettach", "save"]
	req_method = req_dict['Method']
	if req_method == '__init__':
		# Need to decide on what to do with new EMC Creations
		pass
	elif req_method in METHOD_LIST:
		emc = pickle.loads(req_dict['Instance'])
		args = req_dict['Args']
		result = getattr(emc, req_method)(*args)
		if result is not None:
			dump = json.dumps(result)
			sock.send(dump.encode())
		print(req_method,'called with args=', args, 'on', emc)
	elif req_method in ['load', 'list', 'delete']: # These are class methods
		args = req_dict['Args']
		result = getattr(EMController.EMController, req_method)(*args)
		if result is not None:
			dump = json.dumps(result)
			sock.send(dump.encode())
		print(req_method,'called with args=', args)
	else:
		try:
			raise AttributeError('Invalid Attribute')
		except AttributeError:
			print('There is no such attribute in EMController')
		# Not sure if this exception throw causes server/worker
		# to stop accepting and processing requests!

def process_E(req_dict, sock):
	METHOD_LIST = ["updateEvent", "getEvent", "setMap", "getMap"]
	req_method = req_dict['Method']
	if req_method == '__init__': # Event Constructor
		# What to do with new Event Creations?
		pass
	elif req_method in METHOD_LIST:
		ev = pickle.loads(req_dict['Instance'])
		args = req_dict['Args']
		result = getattr(ev, req_method)(*args)
		if result is not None:
			dump = json.dumps(result)
			sock.send(dump.encode())
		print(req_method,'called with args=', args, 'on', ev)
	else:
		try:
			raise AttributeError('Invalid Attribute')
		except AttributeError:
			print('There is no such attribute in EMController')
		# Not sure if this exception throw causes server/worker
		# to stop accepting and processing requests!

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
