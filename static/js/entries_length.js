const pinCodeInput = document.getElementById("pin_code_input");

pinCodeInput.addEventListener("input", function () {
        this.value = this.value.replace(/[^0-9]/g, ""); // Remove non-numeric characters
        if (this.value.length > 6) {
            this.value = this.value.slice(0, 6); // Truncate to 6 characters
        }
    });

function calculateAge() {
    const dobInput = document.getElementById("dob");
    const ageInput = document.getElementById("ageInput");

    if (dobInput.value) {
        const dob = new Date(dobInput.value);
        const today = new Date();

        const age = today.getFullYear() - dob.getFullYear();
        const monthDiff = today.getMonth() - dob.getMonth();

        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
            ageInput.value = age - 1;
        } else {
            ageInput.value = age;
        }
    } else {
        ageInput.value = "";
    }
}
function checkAccountNumbers() {
    var accNumber = document.getElementById("acc_number").value;
    var reAccNumber = document.getElementById("re_acc_number").value;

    var messageContainer4 = document.getElementById("messageContainer4");

    if (accNumber === reAccNumber) {
        messageContainer4.innerHTML = ""; // Clear any previous error message
    } else {
        messageContainer4.innerHTML = "Account numbers do not match.";
    }
}


 var animateButton = function(e) {

e.preventDefault;
//reset animation
e.target.classList.remove('animate');
e.target.classList.add('animate');
setTimeout(function(){
  e.target.classList.remove('animate');
},700);
};

var bubblyButtons = document.getElementsByClassName("bubbly-button");

for (var i = 0; i < bubblyButtons.length; i++) {
bubblyButtons[i].addEventListener('click', animateButton, false);
}