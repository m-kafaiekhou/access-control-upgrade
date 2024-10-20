
function populateDropdown(selectId, start, end) {
    var select = document.getElementById(selectId);
    for (var i = start; i <= end; i++) {
        var option = document.createElement("option");
        option.value = i;
        option.text = i;
        select.add(option);
    }
}

populateDropdown("year1", 1400, 1450);
populateDropdown("year2", 1400, 1450);

var months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"];
var monthSelect1 = document.getElementById("month1");
var monthSelect2 = document.getElementById("month2");

for (var i = 0; i < months.length; i++) {
    var option1 = document.createElement("option");
    var option2 = document.createElement("option");
    option1.value = i + 1;
    option2.value = i + 1;
    option1.text = months[i];
    option2.text = months[i];
    monthSelect1.add(option1);
    monthSelect2.add(option2);
}

populateDropdown("day1", 1, 31);
populateDropdown("day2", 1, 31);


function populateDropdown(selectId, start, end) {
    var select = document.getElementById(selectId);
    for (var i = start; i <= end; i++) {
        var option = document.createElement("option");
        option.value = i;
        option.text = (i < 10 ? '0' : '') + i;
        select.add(option);
    }
}

populateDropdown("hour1", 0, 23);
populateDropdown("hour2", 0, 23);
populateDropdown("minute1", 0, 59);
populateDropdown("minute2", 0, 59);
populateDropdown("second1", 0, 59);
populateDropdown("second2", 0, 59);


let get_image = false;
let get_finger = false;



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

// Add an event listener to the button with id "finger-btn"
document.getElementById("finger-btn").addEventListener("click", function() {
    // if (!get_image) {
        
    //     window.alert("ابتدا چهره را ثبت کنید")
    //     return 
    // }
    console.log(typeof get_image)
    console.log(get_image)
    pid = document.getElementById("PID").value
 
    var url = "/accounts/communication/finger/";

    let csrftoken = getCookie("csrftoken")
  
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrftoken
        }
    });

    $.ajax({
        url: url, 
        type: "POST",
        data: {PID: pid},
        dataType: "json",
        success: (jsonResponse) => {
            console.log(jsonResponse);
            get_finger = true;
            window.alert(jsonResponse.msg)
        },
        error: (jqXHR, textStatus, errorThrown) => {
            console.log("error finger");
            window.alert(jqXHR.responseJSON.msg);
        },
    });

  });


// Add an event listener to the button with id "image-btn"
document.getElementById("image-btn").addEventListener("click", function() {
    pid = document.getElementById("PID").value;

    var url = "/accounts/communication/image/";
    
    let csrftoken = getCookie("csrftoken")

    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrftoken
        }
    });

    $.ajax({
        url: url, 
        type: "POST",
        data: {PID: pid},
        dataType: "json",
        success: (jsonResponse) => {
            console.log("success");
            get_image = true;
            window.alert(jsonResponse.msg);
        },
        error: (jqXHR, textStatus, errorThrown) => {
            window.alert(jqXHR.responseJSON.msg);
            console.log("error face");
        },
    });

  });



function validateForm() {
    console.log(get_image)
    console.log(get_finger)
    if (get_finger && get_image) {
        console.log("1")
        return true
    } else if (!get_image) {
        console.log("2")

        window.alert("ابتدا جهره را ثبت کنید")
        return false
    } else if (!get_finger) {
        console.log("3")

        window.alert("ابتدا اثر انگشت را ثبت کنید")
        return false
    }
    console.log("4")

    return false
}
  