(function() {

  $('.cat-item').hover(
    function() {
      $(this).find('.cat-item-options').removeClass('hidden');
    },
    function() {
      $(this).find('.cat-item-options').addClass('hidden');
  });

})();