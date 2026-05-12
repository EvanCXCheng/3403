'use strict';

const buttons = document.querySelectorAll('[data-scope]');
const tbodyGlobal  = document.getElementById('tbody-global');
const tbodyFriends = document.getElementById('tbody-friends');

function setScope(scope) {
  tbodyGlobal.classList.toggle('hidden', scope !== 'global');
  tbodyFriends.classList.toggle('hidden', scope !== 'friends');

  buttons.forEach((btn) => {
    const active = btn.dataset.scope === scope;
    btn.classList.toggle('bg-surface-bright', active);
    btn.classList.toggle('text-primary', active);
    btn.classList.toggle('text-on-surface-variant', !active);
  });
}

buttons.forEach((btn) => {
  btn.addEventListener('click', () => setScope(btn.dataset.scope));
});

setScope('global');