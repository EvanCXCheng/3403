'use strict';

const loginForm = document.getElementById('user');
const registerForm = document.getElementById('new');

loginForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('userpassword').value;
  // POST login will be wired to Flask in Step 3
  console.log('Login attempt:', username);
});

registerForm.addEventListener('submit', (e) => {
  e.preventDefault();

  const email = document.getElementById('newname').value.trim();
  const password = document.getElementById('newpassword').value;

  if (!isValidEmail(email)) {
    document.getElementById('email_error').textContent = 'Please enter a valid email address.';
    return;
  }
  document.getElementById('email_error').textContent = '';

  if (!isValidPassword(password)) {
    document.getElementById('password_error').textContent =
      'Password must contain uppercase, lowercase, a number, and be 8+ characters.';
    return;
  }
  document.getElementById('password_error').textContent = '';

  // POST register will be wired to Flask in Step 3
  console.log('Register attempt:', email);
});

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPassword(password) {
  return password.length >= 8
    && /[a-z]/.test(password)
    && /[A-Z]/.test(password)
    && /[0-9]/.test(password);
}
