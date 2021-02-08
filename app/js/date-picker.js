$(document).ready(function(){
	$( "#s" ).change(function() {
	  refreshAll()
	});
	$( "#e" ).change(function() {
	  refreshAll()
	});
});

function refresh(url, plotId) {
	req = $.ajax({
		url : url,
		type : "GET",
		data: {s: $("#s").val(), e: $("#e").val()}
	});

	req.done(function(data) {
		$("#"+plotId).fadeOut(100).fadeIn(300);
		Plotly.react(plotId, data, {});     
	});
}