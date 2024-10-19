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
      document.getElementById('search-btn2').addEventListener('click', function() {
        var name = document.getElementById('search-name').value;
        var family = document.getElementById('search-family').value;
        var pid = document.getElementById('search-pid').value;
    
        // Construct the URL with the parameters
        var url = '/accounts/edit-operator/' + '?name=' + name + '&family=' + family + '&pid=' + pid;
    
        // Redirect to the URL
        window.location.href = url;
      });
    });
    
  
  document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('delete-btn2').addEventListener('click', function() {
        pid = document.getElementById("pid").value;
  
        var url = "/accounts/delete-operator/";
        
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
                window.location.href = response.redirect;
            
            },
                          
            error: function(xhr, status, error) {
                console.log(error)
                console.log(xhr.status)
                
            }
        });
        });
    });