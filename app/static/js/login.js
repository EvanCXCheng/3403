'use strict';

const loginForm    = document.getElementById('user');
const registerForm = document.getElementById('new');

// ── Login ──────────────────────────────────────────────────────────────────────
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearErrors();

  const data = new FormData(loginForm);
  data.append('action', 'login');

  const json = await postForm(data);

  if (json.ok) {
    window.location.href = json.redirect;
  } else if (json.error) {
    showError('login_error', json.error);
  } else if (json.errors) {
    mapErrors(json.errors, { email: 'login_error', password: 'login_error' });
  }
});

// ── Register ───────────────────────────────────────────────────────────────────
registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearErrors();

  // Client-side validation before hitting the server
  const email    = document.getElementById('newname').value.trim();
  const password = document.getElementById('newpassword').value;

  if (!isValidEmail(email)) {
    showError('email_error', 'Please enter a valid email address.');
    return;
  }
  if (!isValidPassword(password)) {
    showError('password_error',
      'Password must be 8+ characters and include uppercase, lowercase, and a number.');
    return;
  }

  const data = new FormData(registerForm);
  data.append('action', 'register');

  const json = await postForm(data);

  if (json.ok) {
    window.location.href = json.redirect;
  } else if (json.error) {
    showError('email_error', json.error);
  } else if (json.errors) {
    mapErrors(json.errors, { email: 'email_error', password: 'password_error' });
  }
});

// ── Helpers ────────────────────────────────────────────────────────────────────
async function postForm(formData) {
  try {
    const res = await fetch('/login', { method: 'POST', body: formData });
    return await res.json();
  } catch {
    return { ok: false, error: 'Network error — please try again.' };
  }
}

function showError(id, message) {
  const el = document.getElementById(id);
  if (el) el.textContent = message;
}

function clearErrors() {
  ['login_error', 'email_error', 'password_error'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.textContent = '';
  });
}

function mapErrors(errors, fieldMap) {
  for (const [field, msg] of Object.entries(errors)) {
    showError(fieldMap[field] || 'login_error', msg);
  }
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPassword(password) {
  return password.length >= 8
    && /[a-z]/.test(password)
    && /[A-Z]/.test(password)
    && /[0-9]/.test(password);
}
