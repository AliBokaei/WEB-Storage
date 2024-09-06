function passConfirm() {
  const password1 = document.getElementById("passwordID1").value;
  const password2 = document.getElementById("passwordID2").value;
  const passDiv = document.getElementById("passwordDiv");
  const messageElement = document.getElementById("Message");

  if (password1 === password2) {
    passDiv.classList.remove("error-input-password-box");
    messageElement.textContent = "  Passwords match!";
    messageElement.style.color = "green";
  } else {
    passDiv.classList.add("error-input-password-box");
    messageElement.textContent = "  Passwords do not match!";
    messageElement.style.color = "#FF7474";
  }
}

