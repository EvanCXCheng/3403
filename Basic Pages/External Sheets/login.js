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
  console.log(username, password);
});