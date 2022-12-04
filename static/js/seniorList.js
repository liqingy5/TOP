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


function confirm() {
  const seniors = document.querySelectorAll("div.card");
  var id = 0;
  seniors.forEach((senior) => {
    if (senior.classList.contains("active")) {
      id = senior.id;
    }
  });

  if (id !== 0) {
    console.log(id);
    $.post( "/confirm", {
      selected_senior_id: id
    });

    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/confirm");

    let data = {
      selected_senior_id: id,
    };

    console.log(data);

    xhr.send(data);
  }

}

