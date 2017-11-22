import sys
import kdtree
import math

class LocationTree:
	def __init__(self, lat = (-90,90), lon = (-180,180), next_division = 'lat'):
		self.lat = lat
		self.lon = lon
		self.next_division = next_division
		self.left = None
		self.right = None
		self.events = {}
		if abs(self.lat[1] - self.lat[0]) != 45 or abs(self.lon[1] - self.lon[0]) != 90: #Smallest Rectangles are 45x90 (16 many)
			if next_division == 'lat':
				lat_mid = (self.lat[0] + self.lat[1])/2
				self.left = LocationTree( (self.lat[0],lat_mid), lon, 'lon')
				self.right = LocationTree( (lat_mid, self.lat[1]), lon, 'lon')
			elif next_division == 'lon':
				lon_mid = (self.lon[0] + self.lon[1])/2
				self.left = LocationTree(lat, (self.lon[0], lon_mid), 'lat')
				self.right = LocationTree(lat, (lon_mid, self.lon[1]), 'lat')
		#Note to self: Decide if a point can only be in ONE Rectangle(LocationTree)

	def __contains__(self, point):
		lat, lon = point
		if lat <= self.lat[1] and lat >= self.lat[0] and lon <= self.lon[1] and lon >= self.lon[0]:
			return True
		else:
			return False

	def insertEvent(self, event, point):
		if self.left == None and self.right == None:
			self.events[point] = event
		elif point in self.right:
			self.right.insertEvent(event, point)
		elif point in self.left:
			self.left.insertEvent(event, point)
		else:
			pass #Error Point doesn't exist in the Map OR Tree corrupted

class EventMap:
	def __init__(self):
		self.events = {}
		self.tree = kdtree.create(dimensions = 2)
	
	def insertEvent(self, event, lat, lon):
		point = (lat,lon)
		if point not in self.events:
			self.events[point] = [event]
		else:
			self.events[point].append(event)
		self.tree.add(point)
		if not self.tree.is_balanced:
			self.tree = self.tree.rebalance()

	def deleteEvent(self, id):
		# decide on what id will be
		pass
	
	def eventUpdated(self, id):
		# decide on what id will be
		pass

	def searchbyRect(self, lattl, lontl, latbr, lonbr):
		mid_point = ((lattl + latbr)/2, (lontl + lonbr)/2)
		radius = sum([(x - y)**2 for x,y in zip(mid_point, (lattl,lontl))])
		in_radius = self.tree.search_nn_dist(mid_point, radius + 1) # +1 is for overcoming the within constraint (optional)
		result = []
		for point in in_radius:
			if point[0] in range(latbr, lattl) and point[1] in range(lontl, lonbr):
				result.append(point)
		return result

	def findClosest(self, lat, lon):
		point = (lat, lon)
		return self.events[self.tree.search_nn(point)[0].data]
		
