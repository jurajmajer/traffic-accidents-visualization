$(document).ready(function(){
	$( "#date-picker-start-id" ).change(function() {
	  refreshAll()
	});
	$( "#date-picker-end-id" ).change(function() {
	  refreshAll()
	});
	$( "#date-picker-quick-week-id" ).click(function() {
	  quickItemClicked(7)
	});
	$( "#date-picker-quick-month-id" ).click(function() {
	  quickItemClicked(30)
	});
	$( "#date-picker-quick-year-id" ).click(function() {
	  quickItemClicked(365)
	});
	$( "#date-picker-quick-total-id" ).click(function() {
	  $( "#date-picker-start-id" ).val($( "#date-picker-start-id" ).attr( "min" ))
	  $( "#date-picker-end-id" ).val($( "#date-picker-end-id" ).attr( "max" ))
	  refreshAll()
	});
});

function refresh(url, plotId) {
	req = $.ajax({
		url : url,
		type : "GET",
		data: {s: $("#date-picker-start-id").val(), e: $("#date-picker-end-id").val()}
	});

	req.done(function(data) {
		$("#"+plotId).fadeOut(100).fadeIn(300);
		Plotly.react(plotId, data, {});     
	});
}

function quickItemClicked(days) {
	var lastDay = new Date()
	lastDay.setDate(lastDay.getDate() - 1);
	$( "#date-picker-end-id" ).val(lastDay.toISOString().slice(0, 10))
	var firstDay = new Date()
	firstDay.setDate(firstDay.getDate() - 1 - days);
	$( "#date-picker-start-id" ).val(firstDay.toISOString().slice(0, 10))
	refreshAll()
}
