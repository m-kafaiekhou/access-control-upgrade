function validateForm() {
    var password2 = document.getElementById("password2");
    var password1 = document.getElementById("password1");

    if (password1.value != password2.value) {
        alert("پسورد و تکرار ان باید برابر باشند");
        password2.focus(); // Set focus on the invalid field
        return false; // prevent form submission
    }

    // Password validation with symbol requirement
    var passwordPattern = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&*!])(.{8,})/;
    if (!passwordPattern.test(password1.value)) {
      alert("رمزعبور باید حداقل ۸ کاراکتر و شامل حداقل یک حرف کوچک، یک حرف بزرگ، یک عدد و یک نماد (@، #، $، %، ^، &، *، !) باشد.");
      password1.focus(); // Set focus on the invalid field
      return false; // prevent form submission
    }

    if (!passwordPattern.test(password2.value)) {
      alert("رمزعبور باید حداقل ۸ کاراکتر و شامل حداقل یک حرف کوچک، یک حرف بزرگ، یک عدد و یک نماد (@، #، $، %، ^، &، *، !) باشد.");
      password2.focus(); // Set focus on the invalid field
      return false; // prevent form submission
    }

    // Additional validation logic for username and password complexity
    // ...

    return true; // allow form submission
  }