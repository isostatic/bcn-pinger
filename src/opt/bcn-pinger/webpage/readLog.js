$(function() {
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
