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
        // if (i==59) {
        //     option.selected = true
        // }
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



document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('report-btn').addEventListener('click', function() {
        var downloadWindow = window.open('/accounts/download-report/', '_blank');

        setTimeout(function(){
            downloadWindow.close();
        }, 1000);
        
      });
  });