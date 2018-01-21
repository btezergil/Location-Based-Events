maps = [];

events = [];
eventmarkers = [];

attachedto = undefined;

currentmap = undefined;

selectedevent = undefined;
searched = [];

observers = [];
sent = false;

watchareas = [];

sesskey = undefined;

// Used for getting csrftoken from django
function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
            }
        }
    }
	return cookieValue;
}

// Refresh of the map model in <maps> from server
function loadmaps()
{
	$.getJSON('list', function(data) {
		if (data.result == 'Fail') {
			alert(data.reason);
			return;
		}
		for (var i in data.success.maplist) {
			var v = data.success.maplist[i];
			maps[v.id] = v;
		}

		sesskey = data.success.session_key;
		createwebsocket("ws://127.0.0.1:5678", sesskey, wseventhandler);
		setattach(data.success.attachedmap);

		// now update the maplist <ol> from the model
		updatemapsview();
	});
}

// Refresh the watch areas of observers
function refreshareas() 
{
	clearareas();

	// From loaded observers, create new rectangles
	for (i in observers) {
		if (observers[i].Map_id == attachedto) {
			var lattl = observers[i].lat_topleft;
			var lontl = observers[i].lon_topleft;
			var latbr = observers[i].lat_botright;
			var lonbr = observers[i].lon_botright;

			var bounds = [[lattl, lontl], [latbr, lonbr]];
			var area = L.rectangle(bounds, {color: "blue", weight: 1}).addTo(currentmap);
			watchareas[i] = area;
		}
	}
}

// Set attachmap web view
function setattach(attachedmap)
{
	attachedto = attachedmap.id;
	$('#attachname').html('Attached to ' + attachedmap.name);
	if (attachedto !== "None") {
		$('#detachbutton').show();
		$('#eventaddbutton').show();
		$('#delbutton').attr('disabled', false);
		$('#findbutton').attr('disabled', false);
		$('#searchbutton').attr('disabled', false);
		$('#observeraddbutton').show();
		loadeventsofmap(attachedmap);
		loadobsofsess(attachedmap);
		refreshareas();
	}
	else {
		$('#detachbutton').hide();
		$('#eventaddbutton').hide();
		$('#delbutton').attr('disabled', true);
		$('#findbutton').attr('disabled', true);
		$('#searchbutton').attr('disabled', true);
		$('#observeraddbutton').hide();
	}
}

// Attach to a map
function attachmap()
{
	var strid = $("#maplist li.ui-selected").attr('id');
	if (strid === "None") {
		alert("Please select a valid Map!");
		return;
	}
	var mapid = parseInt(strid);

	$.getJSON('attach/'+mapid, function(data) {
		if (data.result == 'Fail') {
			alert(data.reason);
			return;
		}
		setattach(maps[data.success.id]);
	});
}

// Detach from Map
function detachmap()
{
	$.getJSON('detach/'+attachedto, function(data) {
		if (data.result == 'Fail') {
			alert("Not correctly attached before detach");
			return;
		}

		// Default None Map
		var m = {'id':'None', 'name':'None'};
		setattach(m);
		clearevents();
		clearareas();
		observers = [];
	});
}

// Delete Attached Map
function deletemap()
{
	$.getJSON('delete/'+attachedto, function(data) {
		if (data.result == 'Fail') {
			alert("Not correctly attached before delete");
			return;
		}
		
		var strid = attachedto.toString();
		$("#maplist li[id=" + strid + "]").remove();
		
		maps[attachedto] = undefined;

		// Default None Map
		var m = {'id':'None', 'name':'None'};
		setattach(m);
	});
}

// Find Closest Query
function postfind()
{
	var eid;
	resetmap();
	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});

	data = $("#findform").serialize();
	$.post("findclosest/"+attachedto, data, function (data) {
			if (data.result != "Success") {
				alert(data.reason);
				return;
			}
			eid = data.success.id;
			$('#mapresetbutton').attr('disabled', false);

			const markerHtmlStyles = `background-color: #c30000; 
			width: 2rem;
			height: 2rem;
			display: block;
			left: -1.5rem;
			top: -1.5rem;
			position: relative;
			border-radius: 3rem 3rem 0;
			transform: rotate(45deg);
			border: 1px solid #FFFFFF`

			const highlighticon = L.divIcon({
				className: "highlight",
				iconAnchor: [0, 24],
				labelAnchor: [-6, 0],
				popupAnchor: [0, -36],
				html: `<span style="${markerHtmlStyles}" />`
			})

			var marker = L.marker([events[eid].lat, events[eid].lon], {icon: highlighticon}).addTo(currentmap);
			marker.bindPopup(eventmarkers[eid].getPopup());
			eventmarkers[eid].remove();
			eventmarkers[eid] = marker;
			marker.openPopup();
			searched[eid] = eid;
	});


}

// Search Advanced Query
function postsearch()
{
	var foundevents;
	resetmap();
	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});

	data = $("#searchform").serialize();
	$.post("searchadvanced/"+attachedto, data, function (data) {
			if (data.result != "Success") {
				alert(data.reason);
				return;
			}

			$('#mapresetbutton').attr('disabled', false);
			foundevents = data.success.ids;

			const markerHtmlStyles = `background-color: #c30000; 
			width: 2rem;
			height: 2rem;
			display: block;
			left: -1.5rem;
			top: -1.5rem;
			position: relative;
			border-radius: 3rem 3rem 0;
			transform: rotate(45deg);
			border: 1px solid #FFFFFF`

			const highlighticon = L.divIcon({
				className: "highlight",
				iconAnchor: [0, 24],
				labelAnchor: [-6, 0],
				popupAnchor: [0, -36],
				html: `<span style="${markerHtmlStyles}" />`
			})
			
			for (var i = 0; i < foundevents.length; i++){
				var eid = foundevents[i];
				var marker = L.marker([events[eid].lat, events[eid].lon], {icon: highlighticon}).addTo(currentmap);
				marker.bindPopup(eventmarkers[eid].getPopup());
				eventmarkers[eid].remove();
				eventmarkers[eid] = marker;
				searched[i] = eid;
			}

	});


}

function resetmap()
{
	for (var i = 0; i < searched.length; i++){
		var id = searched[i]
		eventmarkers[id].remove();
		var marker = L.marker([events[id].lat, events[id].lon]).addTo(currentmap);
		marker.bindPopup("<b>Title:</b>" +  events[id].title + "<br><b>Description:</b>"+ events[id].desc + "<br><b>Location:</b>"+ events[id].locname + 
			"<br><b>Categories:</b>"+ events[id].catlist + "<br><b>Start time:</b>"+ events[id].stime + "<br><b>Finish time:</b>"+ events[id].to +
			"<br><button id=\"eventupdatebutton\" value=\"UpdateEvent\" >Update this event</button>" + 
			"<br><button id=\"eventdeletebutton\" value=\"DeleteEvent\" >Delete this event</button>");
		eventmarkers[id] = marker;
	}
	searched = [];
	$('#mapresetbutton').attr('disabled', true);
}

// Update the maps view on the web page
function updatemapsview()
{
	// remove all rows from list
	$("#maplist li").remove();

	// update all rows
	for (id in maps) {
		$("#maplist").append('<li class="ui-widget-content" ' + 'id=' + id + '>'  + maps[id].name  + '</li>')
	}
}

// Clear the observer rectangles on the map
function clearareas()
{
	for (i in watchareas) {
		watchareas[i].remove();
	}
	watchareas = [];
}

function clearevents()
{
	$("#eventlist li").remove();
	for (id in eventmarkers) {
		eventmarkers[id].remove();
	}
	eventmarkers = [];
	events = [];
}

// Refresh of the map model in <maps> from server
function loadeventsofmap(attachedmap)
{
	clearevents();
	mapid = attachedmap.id;
	$.getJSON('listEvents/'+mapid, function(data) {
		if (data.result == 'Fail') {
			alert(data.reason);
			return;
		}
		for (var i in data.success.evlist) {
			var v = data.success.evlist[i];
			events[v.id] = v;
		}

		if (sesskey == null){
			sesskey = data.success.session_key
			createwebsocket("ws://127.0.0.1:5678", sesskey, wseventhandler);
		}

		// now update the eventlist table from the model
		updateeventsview();
	});
}

function loadobsofsess(attachedmap)
{
	mapid = attachedmap.id;
	observers = [];
	$.getJSON('getObs/'+mapid, function(data) {
		if (data.result == 'Fail') {
			alert(data.reason);
			return;
		}
		for (var i in data.success.obslist) {
			var v = data.success.obslist[i];
			observers[v.id] = v;
		}

		// now update the eventlist table from the model
		updateobsview();
	});
}

function updateobsview()
{
	
	// remove all rows from list
	$("#obslist li").remove();

	// update all rows
	for (id in observers) {
		if (observers[id].category == "") observers[id].category = "All";
		$("#obslist").append('<li class="ui-widget-content" ' + 'id=' + id + '>'  + observers[id].category + '</li>');
		
	}
}

// Update the maps view on the web page
function updateeventsview()
{
	
	// remove all rows from list
	$("#eventlist li").remove();

	// update all rows
	for (id in events) {
		var marker = L.marker([events[id].lat, events[id].lon]).addTo(currentmap);
		marker.bindPopup("<b>Title:</b>" +  events[id].title + "<br><b>Description:</b>"+ events[id].desc + "<br><b>Location:</b>"+ events[id].locname + 
						"<br><b>Categories:</b>"+ events[id].catlist + "<br><b>Start time:</b>"+ events[id].stime + "<br><b>Finish time:</b>"+ events[id].to +
						"<br><button id=\"eventupdatebutton\" value=\"UpdateEvent\" >Update this event</button>" + 
						"<br><button id=\"eventdeletebutton\" value=\"DeleteEvent\" >Delete this event</button>");
		marker._eid = id;
		eventmarkers[id] = marker;
		$("#eventlist").append('<li class="ui-widget-content" ' + 'id=' + id + '>'  + events[id].title  + '</li>');
	}
}

// Post addmap request on server
function postevent()
{
	var id;
	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});
	sent = true;

	data = $("#eventaddform").serialize() ;
	$.post("addevent/"+attachedto, data, function (data) {
			if (data.result != "Success") {
				alert(data.reason);
				return;
			}
			var lat = $("#eventaddform input[name=lat]").val()
			var lon = $("#eventaddform input[name=lon]").val()
			var locname = $("#eventaddform input[name=locname]").val()
			var title = $("#eventaddform input[name=title]").val()
			var desc = $("#eventaddform input[name=desc]").val()
			var catlist = $("#eventaddform input[name=catlist]").val()
			var stime = $("#eventaddform input[name=stime]").val()
			var to = $("#eventaddform input[name=to]").val()
			var timetoann = $("#eventaddform input[name=timetoann]").val()

			id = data.success.id;
			events[id] = {'id':id, 'lat':lat, 'lon':lon, 'locname':locname, 'title':title, 'desc':desc, 
							'catlist':catlist, 'stime':stime, 'to':to, 'timetoann':timetoann};

			var marker = L.marker([events[id].lat, events[id].lon]).addTo(currentmap);
			marker.bindPopup("<b>Title:</b>" +  events[id].title + "<br><b>Description:</b>"+ events[id].desc + "<br><b>Location:</b>"+ events[id].locname + 
				"<br><b>Categories:</b>"+ events[id].catlist + "<br><b>Start time:</b>"+ events[id].stime + "<br><b>Finish time:</b>"+ events[id].to +
				"<br><button id=\"eventupdatebutton\" value=\"UpdateEvent\" >Update this event</button>" + 
				"<br><button id=\"eventdeletebutton\" value=\"DeleteEvent\" >Delete this event</button>");
			marker._eid = id;
			eventmarkers[id] = marker;
	});
}

function updevent()
{
	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});
	sent = true;

	data = $("#eventaddform").serialize() ;
	$.post("updevent/"+attachedto+"/"+selectedevent, data, function (data) {
			if (data.result != "Success") {
				alert(data.reason);
				return;
			}
			var lat = $("#eventaddform input[name=lat]").val()
			var lon = $("#eventaddform input[name=lon]").val()
			var locname = $("#eventaddform input[name=locname]").val()
			var title = $("#eventaddform input[name=title]").val()
			var desc = $("#eventaddform input[name=desc]").val()
			var catlist = $("#eventaddform input[name=catlist]").val()
			var stime = $("#eventaddform input[name=stime]").val()
			var to = $("#eventaddform input[name=to]").val()
			var timetoann = $("#eventaddform input[name=timetoann]").val()

			events[selectedevent] = {'id':id, 'lat':lat, 'lon':lon, 'locname':locname, 'title':title, 'desc':desc, 
							'catlist':catlist, 'stime':stime, 'to':to, 'timetoann':timetoann};

			eventmarkers[selectedevent].remove();
			var marker = L.marker([events[selectedevent].lat, events[selectedevent].lon]).addTo(currentmap);
			marker.bindPopup("<b>Title:</b>" +  events[selectedevent].title + "<br><b>Description:</b>"+ events[selectedevent].desc + "<br><b>Location:</b>"+ events[selectedevent].locname + 
				"<br><b>Categories:</b>"+ events[selectedevent].catlist + "<br><b>Start time:</b>"+ events[selectedevent].stime + "<br><b>Finish time:</b>"+ events[selectedevent].to +
				"<br><button id=\"eventupdatebutton\" value=\"UpdateEvent\" >Update this event</button>" + 
				"<br><button id=\"eventdeletebutton\" value=\"DeleteEvent\" >Delete this event</button>");
			marker._eid = selectedevent;
			eventmarkers[selectedevent] = marker;
	});
}

function delevent()
{
	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});
	sent = true;

	$.post("delevent/"+attachedto+"/"+selectedevent, function (data) {
			if (data.result != "Success") {
				alert(data.reason);
				return;
			}

			eventmarkers[selectedevent].remove();
			eventmarkers[selectedevent] = undefined;
			events[selectedevent] = undefined;
	});
}

// Post addmap request on server
function postmap()
{
	var id;
	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});

	data = $("#addform").serialize();
	$.post("addmap", data, function (data) {
			if (data.result != "Success") {
				alert(data.reason);
				return;
			}
			var name = $("#addform input[name=name]").val();

			id = data.success.id;
			maps[id] = {'name':name, 'id':id};

			$("#maplist").append('<li class="ui-widget-content" ' + 'id=' + id + '>'  + maps[id].name  + '</li>')
	});
}

function postobs()
{
	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});

	data = $("#observerform").serialize() ;
	$.post("addobs/"+attachedto, data, function (data) {
			if (data.result != "Success") {
				alert(data.reason);
				return;
			}

			var oid = data.success.id;
			var lattl = $("#observerform input[name=lat_topleft]").val();
			var lontl = $("#observerform input[name=lon_topleft]").val();
			var latbr = $("#observerform input[name=lat_botright]").val();
			var lonbr = $("#observerform input[name=lon_botright]").val();
			var category = $("#observerform input[name=category]").val();

			observers[oid] = {'id':oid, 'lattl':lattl, 'lontl':lontl, 'latbr':latbr, 'lonbr':lonbr, 'category':category};

			//if (category == "") category = "All";
			$("#obslist").append('<li class="ui-widget-content" ' + 'id=' + id + '>'  + category + '</li>')

			var bounds = [[lattl, lontl], [latbr, lonbr]];
			var area = L.rectangle(bounds, {color: "blue", weight: 1}).addTo(currentmap);
			watchareas[oid] = area;
	});
}

function wseventhandler(event) {
	if (sent){
		sent = false;
		return;
	}

	const markerHtmlStyles = `background-color: #c30000; 
			width: 2rem;
			height: 2rem;
			display: block;
			left: -1.5rem;
			top: -1.5rem;
			position: relative;
			border-radius: 3rem 3rem 0;
			transform: rotate(45deg);
			border: 1px solid #FFFFFF`

	const highlighticon = L.divIcon({
		className: "highlight",
		iconAnchor: [0, 24],
		labelAnchor: [-6, 0],
		popupAnchor: [0, -36],
		html: `<span style="${markerHtmlStyles}" />`
	})

	var messages = JSON.parse(event.data);
	for ( var mid in messages) {
		if(messages[mid].tag == 'INSERT'){
			id = messages[mid].eid;
			events[id] = {'id':id, 'lat':messages[mid].lat, 'lon':messages[mid].lon, 'locname':messages[mid].locname, 'title':messages[mid].title, 
				'desc':messages[mid].desc, 'catlist':messages[mid].catlist, 'stime':messages[mid].stime, 'to':messages[mid].to, 'timetoann':messages[mid].timetoann};
			
			for (oid in observers){
				//if (observers[oid].category == 'All') observers[oid].category = '';
				if ( (observers[oid].lon_topleft <= events[id].lon && events[id].lon <= observers[oid].lon_botright) && (observers[oid].lat_botright <= events[id].lat && events[id].lat <= observers[oid].lat_topleft) && (events[id].catlist.includes(observers[oid].category)) ){
					var marker = L.marker([events[id].lat, events[id].lon], {icon: highlighticon}).addTo(currentmap);
					marker.bindPopup("<b>Title:</b>" +  events[id].title + "<br><b>Description:</b>"+ events[id].desc + "<br><b>Location:</b>"+ events[id].locname + 
						"<br><b>Categories:</b>"+ events[id].catlist + "<br><b>Start time:</b>"+ events[id].stime + "<br><b>Finish time:</b>"+ events[id].to +
						"<br><button id=\"eventupdatebutton\" value=\"UpdateEvent\" >Update this event</button>" + 
						"<br><button id=\"eventdeletebutton\" value=\"DeleteEvent\" >Delete this event</button>");
					marker._eid = id;
					eventmarkers[id] = marker;
					searched[id] = id;
					$('#mapresetbutton').attr('disabled', false);
					return;
				}
			}
			var marker = L.marker([events[id].lat, events[id].lon]).addTo(currentmap);
			marker.bindPopup("<b>Title:</b>" +  events[id].title + "<br><b>Description:</b>"+ events[id].desc + "<br><b>Location:</b>"+ events[id].locname + 
				"<br><b>Categories:</b>"+ events[id].catlist + "<br><b>Start time:</b>"+ events[id].stime + "<br><b>Finish time:</b>"+ events[id].to +
				"<br><button id=\"eventupdatebutton\" value=\"UpdateEvent\" >Update this event</button>" + 
				"<br><button id=\"eventdeletebutton\" value=\"DeleteEvent\" >Delete this event</button>");
			marker._eid = id;
			eventmarkers[id] = marker;
			searched[id] = id;
			$('#mapresetbutton').attr('disabled', false);
			return;
		}
		else if(messages[mid].tag == 'MODIFY'){
			id = messages[mid].eid;
			events[id] = {'id':id, 'lat':messages[mid].lat, 'lon':messages[mid].lon, 'locname':messages[mid].locname, 'title':messages[mid].title, 
				'desc':messages[mid].desc, 'catlist':messages[mid].catlist, 'stime':messages[mid].stime, 'to':messages[mid].to, 'timetoann':messages[mid].timetoann};
			
			for (oid in observers){
				//if (observers[oid].category == 'All') observers[oid].category = "";
				if ( (observers[oid].lon_topleft <= events[id].lon && events[id].lon <= observers[oid].lon_botright) && (observers[oid].lat_botright <= events[id].lat && events[id].lat <= observers[oid].lat_topleft) && (events[id].catlist.includes(observers[oid].category)) ){
					eventmarkers[id].remove();	
					var marker = L.marker([events[id].lat, events[id].lon], {icon: highlighticon}).addTo(currentmap);
					marker.bindPopup("<b>Title:</b>" +  events[id].title + "<br><b>Description:</b>"+ events[id].desc + "<br><b>Location:</b>"+ events[id].locname + 
						"<br><b>Categories:</b>"+ events[id].catlist + "<br><b>Start time:</b>"+ events[id].stime + "<br><b>Finish time:</b>"+ events[id].to +
						"<br><button id=\"eventupdatebutton\" value=\"UpdateEvent\" >Update this event</button>" + 
						"<br><button id=\"eventdeletebutton\" value=\"DeleteEvent\" >Delete this event</button>");
					marker._eid = id;
					eventmarkers[id] = marker;
					searched[id] = id;
					$('#mapresetbutton').attr('disabled', false);
					return;
				}
			}
			var marker = L.marker([events[id].lat, events[id].lon]).addTo(currentmap);
			marker.bindPopup("<b>Title:</b>" +  events[id].title + "<br><b>Description:</b>"+ events[id].desc + "<br><b>Location:</b>"+ events[id].locname + 
				"<br><b>Categories:</b>"+ events[id].catlist + "<br><b>Start time:</b>"+ events[id].stime + "<br><b>Finish time:</b>"+ events[id].to +
				"<br><button id=\"eventupdatebutton\" value=\"UpdateEvent\" >Update this event</button>" + 
				"<br><button id=\"eventdeletebutton\" value=\"DeleteEvent\" >Delete this event</button>");
			marker._eid = id;
			eventmarkers[id] = marker;
			searched[id] = id;
			return;
		}
		else if(messages[mid].tag == 'DELETE'){
			id = messages[mid].eid;
			eventmarkers[id].remove();
			eventmarkers[id] = undefined;
			events[id] = undefined;
			return;
		}
	};
}

function createwebsocket(url, myid, handler) 
{
	// create a web socket
	ws = new WebSocket(url);
	ws.onopen = function() {
		// send my id to filter notifications
		ws.send(myid);
	}
	ws.onmessage = handler;
}
                
// Code to execute on document load
$(document).ready(function() {

	var ws;
	
	$("#addform button[name=cancelbutton]").click(function () {
		$("#addblock").fadeOut();
		return false;
	});

	$("#findform button[name=cancelbutton]").click(function() {
		$("#findblock").fadeOut();
		return false;
	});

	$("#searchform button[name=cancelbutton]").click(function() {
		$("#searchblock").fadeOut();
		return false;
	});

	$("#searchbutton").click(function() {
		$("#searchblock").fadeIn();
		$("#searchform :input").each(function (i, elem) {
			elem.value = "";
		});
		
		$("#searchform [name=actionbutton]").unbind();
		$("#searchform [name=actionbutton]").click(function() {
			$("#searchblock").fadeOut();
			postsearch();
			return false;
		});
		
		return false;
	});

	$("#findbutton").click(function() {
		$("#findblock").fadeIn();
		$("#findform :input").each(function (i, elem) {
			elem.value = "";
		});
		
		$("#findform [name=actionbutton]").unbind();
		$("#findform [name=actionbutton]").click(function() {
			$("#findblock").fadeOut();
			postfind();
			return false;
		});
		
		return false;
	});




	$("#addbutton").click(function() {
		$("#addblock").fadeIn();
		$("#addform input[name=name]").val("");
		$("#addform button[name=actionbutton]").unbind();
		$("#addform button[name=actionbutton]")
			.click(function () {
				$("#addblock").fadeOut();
				postmap();
				return false;});

		return false;
	});

	$("#eventaddform button[name=cancelbutton]").click(function () {
		$("#eventaddblock").fadeOut();
		return false;
	});

	$("#eventaddbutton").click(function() {
		if (!attachedto) {
			return;
		}

		if (attachedto === "None") {
			return;
		}
		$("#eventaddblock").fadeIn();
		$("#eventaddform :input").each(function (i, elem) {
			// get movie[elem.name] from model
			elem.value = "";
		});
		$("#eventaddform button[name=actionbutton]").unbind();
		$("#eventaddform button[name=actionbutton]")
			.click(function () {
				$("#eventaddblock").fadeOut();
				postevent();
				return false;});

		return false;
	});

	$(document).on('click', '#eventupdatebutton', function() {
		$("#eventaddblock").fadeIn();
		$("#eventaddform :input").each(function (i, elem) {
			// get movie[elem.name] from model
			elem.value = events[selectedevent][elem.name];
		});
		$("#eventaddform button[name=actionbutton]").unbind();
		$("#eventaddform button[name=actionbutton]")
			.click(function () {
				$("#eventaddblock").fadeOut();
				updevent();
				return false;});

		return false;
	});

	$(document).on('click', '#eventdeletebutton', function() {
		$("#eventdeleteblock .evtitle").text(events[selectedevent].title);
		$("#eventdeleteblock").fadeIn();
		$("#eventdelyesanswer").unbind();
		
		$("#eventdelyesanswer").click(function() {
			$("#eventdeleteblock").fadeOut();
			delevent();
			return false;
		});

		return false;
	});

	$("#eventdelnoanswer").click(function() {
		$("#eventdeleteblock").fadeOut();
		return false;
	});

	$("#delnoanswer").click(function() {
		$("#deleteblock").fadeOut();
		return false;
	});

	$("#delbutton").click(function() {
		if (!attachedto) {
			return;
		}

		if (attachedto === "None") {
			return;
		}

		$("#deleteblock .mapname").text(maps[attachedto].name);
		$("#deleteblock").fadeIn();
		$("#delyesanswer").unbind();
		
		$("#delyesanswer").click(function() {
			$("#deleteblock").fadeOut();
			deletemap();
			return false;
		});

		return false;
	});

	$("#attachbutton").click(function() {
		if (! $("#maplist li.ui-selected").attr('id')) {
			return;
		}
	
		attachmap();
		return false;
	});

	$("#mapresetbutton").click(function() {
		
		resetmap();
	});

	$("#detachbutton").click(function () {
		if (!attachedto) {
			return;
		}

		if (attachedto === "None") {
			return;
		}

		detachmap();
		return false;
	});

	$("#observeraddbutton").click(function() {
		if (!attachedto) {
			return;
		}

		if (attachedto === "None") {
			return;
		}
		$("#observerblock").fadeIn();
		$("#observerform :input").each(function (i, elem) {
			// get movie[elem.name] from model
			elem.value = "";
		});
		$("#observerform button[name=actionbutton]").unbind();
		$("#observerform button[name=actionbutton]")
			.click(function () {
				$("#observerblock").fadeOut();
				postobs();
				return false;});

		return false;
	});
	
	loadmaps();


	currentmap = L.map('leafletmap').setView([39.891, 32.783], 17);
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(currentmap);
	currentmap.on('popupopen', function (e) {
		selectedevent = e.popup._source._eid });

	// Selected callback
	$( function() {
		$( "#maplist" ).selectable({
			selected : function(event, ui) {
				 if ($(ui.selected).hasClass('selectedfilter')) {
					$(ui.selected).removeClass('selectedfilter').siblings().removeClass("selectedfilter");
					$(ui.selected).removeClass('ui-selected').siblings().removeClass("ui-selected");
					$("#attachbutton").attr('disabled', true);
				 }
	
				else {
					$(ui.selected).addClass('selectedfilter').siblings().removeClass("selectedfilter");
					$(ui.selected).addClass("ui-selected").siblings().removeClass("ui-selected");
					$("#attachbutton").attr('disabled', false);
				}
			}
		});
	});

});
