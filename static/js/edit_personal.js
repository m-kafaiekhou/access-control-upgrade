function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Extract the CSRF token value from the cookie
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('search-btn').addEventListener('click', function() {
      var name = document.getElementById('search-name').value;
      var family = document.getElementById('search-family').value;
      var pid = document.getElementById('search-pid').value;
  
      // Construct the URL with the parameters
      var url = '/accounts/edit-personel/' + '?name=' + name + '&family=' + family + '&pid=' + pid;
  
      // Redirect to the URL
      window.location.href = url;
    });
  });
  

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('delete-btn').addEventListener('click', function() {
      pid = document.getElementById("pid").value;
      
      var url = "/accounts/delete-personel/";
      
      let csrftoken = getCookie("csrftoken")

      $.ajaxSetup({
          headers: {
              'X-CSRFToken': csrftoken
          }
      });

      $.ajax({
          url: url, 
          type: "POST",
          data: {pid: pid},
          dataType: 'json',
          success: (response) => {
              window.alert(response.msg)
              window.location.href = response.redirect;
          
          },
                        
          error: function(xhr) {
              console.log(xhr.responseJSON.msg)
              window.alert(xhr.responseJSON.msg)
              
          }
      });
      });
  });

  document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('delete-face').addEventListener('click', function() {
      pid = document.getElementById("pid").value;

      var url = "/accounts/delete-face/";
      
      let csrftoken = getCookie("csrftoken")

      $.ajaxSetup({
          headers: {
              'X-CSRFToken': csrftoken
          }
      });

      $.ajax({
          url: url, 
          type: "POST",
          data: {pid: pid},
          dataType: 'json',
          success: (response) => {
            window.alert(response.msg);
          
          },
                        
          error: (xhr) => {
            window.alert(xhr.responseJSON.msg);
        },
      });
      });
  });


  document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('delete-finger').addEventListener('click', function() {
      pid = document.getElementById("pid").value;

      var url = "/accounts/delete-finger/";
      
      let csrftoken = getCookie("csrftoken")

      $.ajaxSetup({
          headers: {
              'X-CSRFToken': csrftoken
          }
      });

      $.ajax({
          url: url, 
          type: "POST",
          data: {pid: pid},
          dataType: 'json',
          success: (response) => {
              window.alert(response.msg);
          
          },
                        
          error: (xhr) => {
            window.alert(xhr.responseJSON.msg);
        },
      });
      });
  });

  function validateForm() {
    console.log("in form val")
    var time = document.getElementById("time").value;
    var date = document.getElementById("date").value;

    var timePattern = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
    var datePattern = /^(14|13|15)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/;

    if (!time.match(timePattern)) {
        alert("زمان باید به فرمت ساعت:دقیقه باشد. ساعت باید بین 00 تا 23 و دقیقه باید بین 00 تا 59 باشد.");
        return false;
    }

    if (!date.match(datePattern)) {
        alert("تاریخ باید به فرمت سال-ماه-روز باشد. ماه باید بین 01 تا 12 و روز باید بین 01 تا 31 باشد.");
        return false;
    }

    return true;
}


document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('show-image').addEventListener('click', function(event) {
    const pid = this.getAttribute('data-pid');

    console.log(pid)
    var url = "/accounts/show-image/";
    
    let csrftoken = getCookie("csrftoken")

    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrftoken
        }
    });

    $.ajax({
        url: url, 
        type: "POST",
        data: {pid: pid},
        dataType: 'json',
        success: (response) => {
            console.log(response.msg);
        
        },
                      
        error: (xhr) => {
          window.alert(xhr.responseJSON.msg);
      },
    });
    });
});


document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('show-finger').addEventListener('click', function(event) {
    const pid = this.getAttribute('data-pid');

    console.log(pid)
    var url = "/accounts/show-finger/";
    
    let csrftoken = getCookie("csrftoken")

    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrftoken
        }
    });

    $.ajax({
        url: url, 
        type: "POST",
        data: {pid: pid},
        dataType: 'json',
        success: (response) => {
            window.alert(response.msg);
        
        },
                      
        error: (xhr) => {
          window.alert(xhr.responseJSON.msg);
      },
    });
    });
});