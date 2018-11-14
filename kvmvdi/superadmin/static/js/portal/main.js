$( ".item-nav" ).hover(
  function() {
    $(this).children().css( "color", "#60bee5" );
  }, function() {
    $(this).children().css( "color", "#727678" );
  }
);
$(".collapsed").click(function(){

    $(this).find('.rotate').toggleClass("down"); 
});
$( ".add i" ).hover(
  function() {
    $('.add').find('img').css('display','none');
  }, function() {
    $('.add').find('img').css('display','');
  }
);
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});
