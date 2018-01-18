maps = [];

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

// refresh of the map model in <maps> from server
function loadmaps()
{
	$.getJSON('list', function(data) {
		if (data.result == 'Fail') {
			alert(data.reason);
			return;
		}
		for (var i in data.maplist) {
			var v = data.maplist[i];
			maps[v.id] = v;
		}

		// now update the maplist <ol> from the model
		updatemapsview();
	});
}

// Update the maps view on the web page
function updatemapsview()
{
	// remove all rows from list
	$("#maplist li").remove();

	// update all rows
	for (id in maps) {
		$("#maplist").append('<li class="ui-widget-content">' + maps[id].name  + '</li>')
	}
}

// Post add request on server
function postmap()
{
	// TODO: Complete Implementation
}

// Code to execute on document load
$(document).ready(function() {
	// TODO: Add button actions
	
	loadmaps();
});
