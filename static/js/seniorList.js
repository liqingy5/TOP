$(document).ready(function () {
  // Card Multi Select
  $('input[type=checkbox]').click(function () {
    if ($(this).parent().hasClass('active')) {
      $(this).parent().removeClass('active');
    }
    else
    {
      $(this).parent().parent().find('input[type=checkbox]').prop( "checked", false );
      $(this).parent().parent().children().removeClass('active');
      $(this).parent().addClass('active');
      $(this).prop( "checked", true );
    }
  });
});