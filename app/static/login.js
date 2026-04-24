const user = document.getElementById('user');
const register = document.getElementById('new');

user.addEventListener('submit', (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('userpassword').value;
  console.log(username, password);
});

register.addEventListener('submit', (e) => {
  e.preventDefault();
  const username = document.getElementById('newname').value;
  const password = document.getElementById('newpassword').value;

  if (!valid_email(username)) {
    document.getElementById("email_error").textContent =
    "Please enter a valid email address.";
    return;
  }
  document.getElementById("email_error").textContent = "";

  if (!valid_password(password)) {
    document.getElementById("password_error").textContent =
    "Password must contain uppercase, lowercase, number and be 8+ characters";
    return;
  }

  document.getElementById("password_error").textContent = "";
  console.log(username, password);
});

function valid_password (password) {
  if (password.length < 8) {
    return false;
  }
  if (!/[a-z]/.test(password)) {
    return false;
  }
  if (!/[A-Z]/.test(password)) {
    return false;
  }
  if (!/[0-9]/.test(password)) {
    return false;
  }

  return true;
}

function valid_email(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}