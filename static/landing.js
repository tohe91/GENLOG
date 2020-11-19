var interval;
  $( document ).ready(function() {
    update();
    clearInterval(interval);
    interval = setInterval(update, 2000);
});

function startInterval() {
    clearInterval(interval);
    interval = setInterval(update, 2000);
  }
  function update() {
    
    $.ajax({
        url: "/state_eval",
        type: "get",
        data: {},
        success: function(response) {
            console.log(response.table);
          $('#logs').html(response.logs);
          $('#runs').html(response.runs);
        },
          error: function(xhr) {
          
        }
      });
    }
  
