document.addEventListener('DOMContentLoaded', function() {
    var sendOTPButton = document.getElementById('sendOTPButton');
    var verifyOTPButton = document.getElementById('verifyOTPButton');
    var otpSection = document.getElementById('otpSection');
    var otpInput = document.getElementById('otp');
    var submitButton = document.getElementById('submitButton');
    var sessionID;
    var messageContainer = document.getElementById('messageContainer'); // Element to display messages
    var otpSent = false;

    sendOTPButton.addEventListener('click', function() {
        var countryCode = document.getElementById('countriesCode').value;
        var contactNumber = document.getElementById('contact').value;
        sendOTP("" + countryCode + contactNumber);
    });

    verifyOTPButton.addEventListener('click', function() {
        var enteredOTP = otpInput.value;
        verifyOTP(sessionID, enteredOTP);
    });

    function sendOTP(contactNumber) {
        var xhr = new XMLHttpRequest();
        var url = '/send-otp';
        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.hasOwnProperty('sessionID') && response.hasOwnProperty('otp')) {
                    sessionID = response.sessionID;
                    otpSection.style.display = 'block';
                    sendOTPButton.disabled = true;
                    verifyOTPButton.disabled = false;
                    otpInput.focus();
                    messageContainer.textContent = ' Successfully send OTP to your mobile number.';
                } else if (response.hasOwnProperty('error')) {
                    messageContainer.textContent = 'Failed to send OTP. Please try again.';
                }
            }
        };
        var data = JSON.stringify({ 'contactNumber': contactNumber });
        xhr.send(data);
    }

    function verifyOTP(sessionID, enteredOTP) {
        var xhr = new XMLHttpRequest();
        var url = '/verify-otp';
        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.hasOwnProperty('result') && response.result) {
                    verifyOTPButton.disabled = true;
                    submitButton.disabled = false;
                    messageContainer1.textContent = 'Entered OTP is correct.';
                } else {
                    messageContainer1.textContent = 'Entered OTP is wrong. Please try again.';
                }
            }
        };
        var data = JSON.stringify({ 'sessionID': sessionID, 'enteredOTP': enteredOTP });
        xhr.send(data);
    }
});
