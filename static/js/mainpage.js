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


function getLastPerson() {
    $.ajax({
        url: '/accounts/get-last-person/', 
        type: "GET",
        dataType: "json",
        success: (jsonResponse) => {
            let fullname = jsonResponse.fullname
            let phone = jsonResponse.phone
            let permit = jsonResponse.permit
            let permitDate = jsonResponse.expire_date

            

            document.getElementById("fullname").value = fullname
            document.getElementById("phone").value = phone
            document.getElementById("permit").value = permit
            document.getElementById("permit-date").value = permitDate
        },
        error: () => console.log("error occurred"),
    });
}

document.getElementById("checkboxInput").addEventListener("click", function() {
    var url = "/accounts/door-com/";
      
    let csrftoken = getCookie("csrftoken")

    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrftoken
        }
    });

    $.ajax({
        url: url, 
        type: "POST",
        data: {door: this.checked},
        dataType: 'json',
        success: (response) => {
            console.log("Checkbox is clicked! Current value:", this.checked);
        
        },
                    
        error: function(xhr, status, error) {
            console.log(error)
            console.log(xhr.status)
            
        }
    });
  });


//   document.getElementById("checkboxInput1").addEventListener("click", function() {
//     var url = "/accounts/total-com/";
      
//     let csrftoken = getCookie("csrftoken")

//     $.ajaxSetup({
//         headers: {
//             'X-CSRFToken': csrftoken
//         }
//     });

//     $.ajax({
//         url: url, 
//         type: "POST",
//         data: {total: this.checked},
//         dataType: 'json',
//         success: (response) => {
//             console.log("Checkbox is clicked! Current value:", this.checked);
        
//         },
                    
//         error: function(xhr, status, error) {
//             console.log(error)
//             console.log(xhr.status)
            
//         }
//     });
//   });


  function getAlarm() {
    $.ajax({
        url: '/accounts/get-alarm/', 
        type: "GET",
        dataType: "json",
        success: (jsonResponse) => {
            let alarm1 = jsonResponse.alarm1
            let alarm2 = jsonResponse.alarm2

            if (alarm1) {
                window.alert("درب اتاق سرور باز است")
            } else if (alarm2) {
                window.alert("قفل اتاق سرور باز است")
            }
        },
        error: () => console.log("error occurred"),
    });
}

function intervalFunction () {
    getLastPerson();
    getAlarm();
}


setInterval(intervalFunction, 8000)


