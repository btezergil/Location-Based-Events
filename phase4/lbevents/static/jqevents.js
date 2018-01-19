maps = [];

attachedto = undefined;

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
}

// Attach to a map
function attachmap()
{
	$.getJSON('attach', function(data) {
		if (data.result == 'Fail') {
			alert(data.reason);
			return;
		}
		attachedto = data.success.id;
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

			$("#maplist").append('<li class="ui-widget-content">' + maps[id].name + '</li>')
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
	
	loadmaps();

	// Listen to Select changes
	$("#maplist").selectable({
		selected: function(event, ui) {
			if ($(ui.selected).attr('id')) {
				$("#attachbutton").attr('disabled', false);
			}
			else {
				$("#attachbutton").attr('disabled', true);
			}
		}
	});

});
