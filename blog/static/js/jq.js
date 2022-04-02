
//code for slider --> like news ticker
var interval = setInterval(startTicker,4000);

function startTicker(){
    //the first li elem slides up
    $("#all_tweets ul:visible:first").slideUp('slow',function(){
        //removed from ul and slide down
        $(this).appendTo($('#all_tweets')).slideDown('slow');
    });
}
//clears setInterval
function stopTicker(){
    clearInterval(interval);
}

$(document).ready(function () {
    startTicker();
    $("#all_tweets").hover(function () {
            // over
            stopTicker();
        }, function () {
            // out
            startTicker();
            interval= setInterval(startTicker,4000);
        }
    );
});
$(document).ready(function(){
        $("li:contains('Economic Times'),li:contains('The New York Times'),li:contains('Hindustan Times'),li:contains('Times of India'),li:contains('TOI India'),li:contains('ET NOW'),li:contains('DNA'),li:contains('ANI'),li:contains('Firstpost')").parent().addClass("news");
        $("li:contains('ET Panache'),li:contains('Soundarya Sharma'),li:contains('Amitabh Bachchan'),li:contains('Anupam Kher'),li:contains('Radhika Apte'),li:contains('Disha Patani'),li:contains('taapsee pannu'),li:contains('Narendra Modi')").parent().addClass("social");
        $("li:contains('Finshots')").parent().addClass("financial");
        $("#filter a").click(function(){
                $("#filter .current").removeClass("current");
                $(this).parent().addClass("current");
                var filterValue = $(this).text().toLowerCase();
				$("#all_tweets ul").fadeIn(10);
				if (filterValue != "all")
				{
					$("#all_tweets ul").not("." + filterValue).fadeOut(10);
				}
            });

})
