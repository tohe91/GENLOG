var interval;
  $( document ).ready(function() {
    update();
    clearInterval(interval);
    interval = setInterval(update, 2000);

});

var logs = '';
var runs = '';

function startInterval() {

    clearInterval(interval);
    interval = setInterval(update, 2000);
  }

  function update() {
    
    $.ajax({
        url: "state_eval",
        type: "get",
        data: {},
        success: function(response) {
          if (logs != response.logs) {
            $('#logs').html(response.logs);
            logs = response.logs;
          }
          if (runs != response.runs) {
            $('#runs').html(response.runs);
            runs = response.runs;
          }
          console.log(response.hold);
          if (response.hold == true) {
            $("#start").prop('disabled', true);
          } else {
            $("#start").prop('disabled', false);
          }
        },
          error: function(xhr) {
          
        }
      });
    }
  
