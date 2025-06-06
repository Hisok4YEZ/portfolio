(function(document, window, $){
  $(document).ready(function(){
    // Charger dynamiquement la page d'accueil
$("#home-content").load("pages/home.html");

    var $header = $('header');
    function headerAnchors(){
      var pageDirection = '';
      var thisElement;
      var timeout;
      $header.find('nav li a').click(function(event){
        event.preventDefault();
        $('.cube').removeClass('reverse-' + pageDirection);
        thisElement = $(this);
        pageDirection = thisElement.data('direction');
        thisElement.parent().addClass('active').siblings().removeClass('active');
        $('.cube').addClass('reverse-' + pageDirection);
        $header.addClass('go-out');
        $('#wrap').addClass('active');
        clearTimeout(timeout);
        timeout = setTimeout(function(){
          $header.removeClass('go-out');
          $('#wrap').removeClass('active');
        }, 1000);
      });
    }
    headerAnchors();
  });
})(document, window, jQuery);
