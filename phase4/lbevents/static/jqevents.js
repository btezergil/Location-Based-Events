maps = [];

events = [];

attachedto = undefined;

currentmap = undefined;

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

		setattach(data.success.attachedmap);

		// now update the maplist <ol> from the model
		updatemapsview();
	});
}

// Set attachmap web view
function setattach(attachedmap)
{
	attachedto = attachedmap.id;
	$('#attachname').html('Attached to ' + attachedmap.name);
	if (attachedto !== "None") {
		$('#detachbutton').show();
		$('#delbutton').attr('disabled', false);
	}
	else {
		$('#detachbutton').hide();
		$('#delbutton').attr('disabled', true);
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
		loadeventsofmap(maps[data.success.id]);
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

// Refresh of the map model in <maps> from server
function loadeventsofmap(attachedmap)
{
	mapid = attachedmap.id
	$.getJSON('listEvents/'+mapid, function(data) {
		if (data.result == 'Fail') {
			alert(data.reason);
			return;
		}
		for (var i in data.success.evlist) {
			var v = data.success.evlist[i];
			events[v.id] = v;
		}

		// now update the eventlist table from the model
		updateeventsview();
	});
}

// Update the maps view on the web page
function updateeventsview()
{
	// remove all rows from list
	$("#eventlist li").remove();

	// update all rows
	for (id in events) {
		$("#eventlist").append('<li class="ui-widget-content" ' + 'id=' + id + '>'  + events[id].title  + '</li>')
	}
}

// Post addmap request on server
function postmap()
{
	var id;
	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});

	data = $("#addform").serialize() ;
	$.post("addmap", data, function (data) {
			if (data.result != "Success") {
				alert(data.reason);
				return;
			}
			var name = $("#addform input[name=name]").val()

			id = data.success.id;
			maps[id] = {'name':name, 'id':id};

			$("#maplist").append('<li class="ui-widget-content" ' + 'id=' + id + '>'  + maps[id].name  + '</li>')
	});
}

// Code to execute on document load
$(document).ready(function() {

	$("#addform button[name=cancelbutton]").click(function () {
		$("#addblock").fadeOut();
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
	
	loadmaps();

	currentmap = L.map('leafletmap').setView([39.891, 32.783], 17);
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(currentmap);

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
