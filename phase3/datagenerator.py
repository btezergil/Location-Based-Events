#import sys
#sys.path.append('~/Desktop/CENG445/phase3/lbevents')


from generate import generateone
#from lbevents.models import Event, EventMap

for j in range(0,5):
    m = EventMap.objects.get(id=j)
    for i in range(0,4):
        evdict = generateone()
        m.event_set.create(lon=evdict['lon'], lat=evdict['lat'], locname=evdict['locname'], title=evdict['title'], desc=evdict['desc'], catlist=evdict['catlist'], stime=evdict['stime'], to=evdict['to'], timetoann=evdict['timetoann'])

