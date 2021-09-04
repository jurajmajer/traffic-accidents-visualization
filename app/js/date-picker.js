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

const monthNames = ["jan", "feb", "mar", "apr", "máj", "jún", "júl", "aug", "sep", "okt", "nov", "dec"
];

function refresh(url, plotId) {
    s_km_val = -1;
    e_km_val = -1;
    if($('#slider-range').length) {
        s_km_val = $("#slider-range").slider("values")[0];
        e_km_val = $("#slider-range").slider("values")[1];
    }
	req = $.ajax({
		url : url,
		type : "GET",
		data: {s: $("#date-picker-start-id").val(), e: $("#date-picker-end-id").val(),
        	s_km: s_km_val, e_km: e_km_val}
	});

	req.done(function(data) {
		$("#"+plotId).fadeOut(100).fadeIn(300);
		Plotly.react(plotId, data, {});
		d = document.getElementById('date-picker-start-id').valueAsDate
		$("#"+plotId+"-start-date-label").text(d.getDate().toString().padStart(2, "0") + " " + monthNames[d.getMonth()] + " " + d.getFullYear());
		d = document.getElementById('date-picker-end-id').valueAsDate
		$("#"+plotId+"-end-date-label").text(d.getDate().toString().padStart(2, "0") + " " + monthNames[d.getMonth()] + " " + d.getFullYear());
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
