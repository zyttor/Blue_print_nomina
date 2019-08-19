$( document ).ready(function() {
  var api_url = 'http://127.0.0.1:3000/ws_nivel'
  var key = '5b578yg9yvi8sogirbvegoiufg9v9g579gviuiub8' // not real

    $.ajax({
        url: api_url + "?key=" + key + " &q=" + $( this ).text(),
        contentType: "application/json",
        dataType: 'json',
        success: function(result){
            console.log(result);
        }
    })

});