$(function() {
	$("#list").tablesorter({
		widgets: ["zebra", "filter"],
	});
	$(".traceroute").click(function () {
		var dte = $(this).attr("date");
		var ip = $(this).attr("ip");
		var url = "getTraceroute.cgi?log=" + encodeURIComponent(ip) + "&date=" + encodeURIComponent(dte);
		var toFill = $(this).next();
		$(this).hide();
		console.log("get " + url);
		$.get(url, function(d) {
			$(toFill).html(d);
			$(toFill).show();
		});
		return false;
	});
	$(".expand").click(function () {
		if ($(this).text() == "+") {
			$(this).next().show();
			doDate($(this).next());
			$(this).text("-");
		} else {
			$(this).next().hide();
			$(this).text("+");
		}
		return false;
	});
	$(".loading").hide();
	$(".expand").show();
});

function doDate(e) {
	$(e).find(".toDate").each(function (i) {
		var secs = $(this).text();
		console.log("convert " + secs);
		var dte = new Date(secs * 1000);
		$(this).text(dte.toISOString().substring(11,19) + " GMT"); // Doesn't javascript have a built in dateformat?
		$(this).removeClass("toDate");
	});
}
