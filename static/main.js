  var interval;
  var state = '';
  $( document ).ready(function() {
    update();
    clearInterval(interval);
    interval = setInterval(update, 2000);
});
 
  function startInterval() {
    console.log('Interval started');
    clearInterval(interval);
    interval = setInterval(update, 2000);
  }

  
  function update() {
    
    $.ajax({
        url: "/state",
        type: "get",
        data: {},
        success: function(response) {
          state = response;
          console.log(state);
          if (state != 'start') {
            $.ajax({
        url: "/column1",
        type: "get",
        data: {},
        success: function(response) {
          $("#column1").html(response);

        },
        error: function(xhr) {
          
        }
      });

      $.ajax({
        url: "/column2",
        type: "get",
        data: {},
        success: function(response) {
          $("#column2").html(response);
          if(state == 'extract') {
            $("#column2").append('<div class="loader"></div>');
          }
        },
        error: function(xhr) {
          
        }
      });

      $.ajax({
        url: "/column3",
        type: "get",
        data: {},
        success: function(response) {
          $("#column3").html(response);
          if(state == 'resample') {
            $("#column3").append('<div class="loader"></div>');
          }
        },
        error: function(xhr) {
          
        }
      });

      $.ajax({
        url: "/column4",
        type: "get",
        data: {},
        success: function(response) {
          $("#column4").html(response);
          if(state == 'train') {
            $("#column4").append('<div class="loader"></div>');
          }
        },
        error: function(xhr) {
          
        }
      });

      $.ajax({
        url: "/column5",
        type: "get",
        data: {},
        success: function(response) {
          $("#column5").html(response);
          if(state == 'gen') {
            $("#column5").append('<div class="loader"></div>');
          }
        },
        error: function(xhr) {
          
        }
      });
          }
          if (state == 'end') {
            $(".loader").remove();
            
            clearInterval(interval);
          }
        },
        error: function(xhr) {
          
        }
      });

    
}
