$(function() {
	$(".expand").click(function () {
		if ($(this).text() == "+") {
			$(this).next().show();
			$(this).text("-");
		} else {
			$(this).next().hide();
			$(this).text("+");
		}
		return false;
	});
});
