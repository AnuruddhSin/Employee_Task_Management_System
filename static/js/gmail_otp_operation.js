function send_otp_email() {
    var email = document.getElementById("email").value;
    $.ajax({
        url: "/send-otp-email",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ "email": email }),
        success: function (response) {
            messageContainer2.textContent = 'OTP sent to your Gmail number Successfully.';
            document.getElementById("generateBtn").disabled = true;
            document.getElementById("otp1").disabled = false;
            document.getElementById("verifyBtn").disabled = false;
            document.getElementById("generatedOTP").value = response.generated_otp;
        },
        error: function (xhr, status, error) {
            messageContainer2.textContent = 'Failed to send OTP. Please try again.';
        }
    });
}

function verify_otp_email() {
    var otp1 = document.getElementById("otp1").value;
    var generatedOTP = document.getElementById("generatedOTP").value;
    $.ajax({
        url: "/verify-otp-email",
        method: "POST",
        data: { otp1: otp1, generated_otp: generatedOTP },
        success: function (response) {
            if (response === "Access Granted") {
                messageContainer3.textContent = 'Entered OTP is correct.';
                document.getElementById("verifyBtn").disabled = true;

            } else {
                messageContainer3.textContent = 'Entered OTP is wrong. Please try again.';
            }
        },
        error: function (xhr, status, error) {
            messageContainer3.textContent="Failed to verify Gmail OTP. Please try again.";
        }
    });
}
