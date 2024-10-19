function populateDropdown(selectId, start, end) {
    var select = document.getElementById(selectId);
    for (var i = start; i <= end; i++) {
        var option = document.createElement("option");
        option.value = i;
        option.text = i;
        select.add(option);
    }
}

populateDropdown("year", 1400, 1450);

var months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"];
var monthSelect = document.getElementById("month");

for (var i = 0; i < months.length; i++) {
    var option = document.createElement("option");
    option.value = i + 1;
    option.text = months[i];
    monthSelect.add(option);
}

populateDropdown("day", 1, 31);


function validateForm() {
    console.log("in validateForm")
    var username = document.getElementById("username");
    var password = document.getElementById("password1");

    // Username validation
    var usernamePattern = /^[a-zA-Z0-9_]{4,}$/;
    if (!usernamePattern.test(username.value)) {
      console.log("in username")
      alert("نام کاربری باید حداقل ۴ کاراکتر باشد و فقط شامل حروف، اعداد و _ باشد.");
      username.focus(); // Set focus on the invalid field
      return false; // prevent form submission
    }

    // Password validation with symbol requirement
    var passwordPattern = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&*!])(.{8,})/;
    if (!passwordPattern.test(password.value)) {
      console.log("in password")
      alert("رمزعبور باید حداقل ۸ کاراکتر و شامل حداقل یک حرف کوچک، یک حرف بزرگ، یک عدد و یک نماد (@، #، $، %، ^، &، *، !) باشد.");
      password.focus(); // Set focus on the invalid field
      return false; // prevent form submission
    }

    // Additional validation logic for username and password complexity
    // ...
    console.log("before true")
    return true; // allow form submission
  }