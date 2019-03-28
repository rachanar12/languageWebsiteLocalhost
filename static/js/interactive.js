$(document).ready(function(){
  $(window).on('load', function () {
    var a = document.getElementById("brain").contentDocument.getElementById("brainImage");
    var frontal = a.getElementById("frontal");
    var parietal = a.getElementById("parietal");
    var temporal = a.getElementById("temporal");
    var occipital = a.getElementById("occipital");
        $(frontal).mouseover(function() {
          $(".instructions").addClass("no_text");
          $("#frontalText").toggleClass("no_text");
        })
         $(frontal).mouseleave(function() {
          $("#frontalText").addClass("no_text");
          $(".instructions").removeClass("no_text");
      })
         $(parietal).mouseover(function() {
          $(".instructions").addClass("no_text");
          $("#parietalText").toggleClass("no_text");
        })
         $(parietal).mouseleave(function() {
          $("#parietalText").addClass("no_text");
          $(".instructions").removeClass("no_text");
      })
         $(temporal).mouseover(function() {
          $(".instructions").addClass("no_text");
          $("#temporalText").toggleClass("no_text");
        })
         $(temporal).mouseleave(function() {
          $("#temporalText").addClass("no_text");
          $(".instructions").removeClass("no_text");
      })
         $(occipital).mouseover(function() {
          $(".instructions").addClass("no_text");
          $("#occipitalText").toggleClass("no_text");
        })
         $(occipital).mouseleave(function() {
          $("#occipitalText").addClass("no_text");
          $(".instructions").removeClass("no_text");
      })
  })
})

  window.onload = (function(){

    var tweet = document.getElementById("tweet");
    var id = tweet.getAttribute("tweetID");

    twttr.widgets.createTweet(
      id, tweet, 
      {
        conversation : 'none',    // or all
        linkColor    : '#cc0000', // default is blue
        theme        : 'light'    // or dark
      })
    .then (function (el) {
      el.contentDocument.querySelector(".footer").style.display = "none";
    });

  });

$(".box").mouseover(function(){
  $(".figure",this).css("opacity","0.3");
  $(".figure-label",this).css("visibility","visible");
  });
$(".box").mouseleave(function(){
  $(".figure",this).css("opacity","1");
  $(".figure-label",this).css("visibility","hidden");
  });