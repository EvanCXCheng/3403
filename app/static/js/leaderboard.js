'use strict';

const buttons = document.querySelectorAll('[data-scope]');
const tbody   = document.getElementById('leaderboard-body');

function setActiveButton(activeButton) {
  buttons.forEach((button) => {
    button.classList.remove('bg-surface-bright', 'text-primary');
    button.classList.add('text-on-surface-variant');
  });
  activeButton.classList.add('bg-surface-bright', 'text-primary');
  activeButton.classList.remove('text-on-surface-variant');
}

buttons.forEach((btn) => {
  btn.addEventListener('click', () => {
    setActiveButton(btn);
    fetchLeaderboard(btn.dataset.scope);
  });
});

if (buttons.length > 0) {
  const defaultButton = document.querySelector('[data-scope="global"]') || buttons[0];
  setActiveButton(defaultButton);
  fetchLeaderboard(defaultButton.dataset.scope);
}

async function fetchLeaderboard(scope) {
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="5" class="py-10 text-center text-on-surface-variant">Loading…</td></tr>';

  try {
    const res  = await fetch(`/api/leaderboard?scope=${encodeURIComponent(scope)}`);
    const rows = await res.json();
    renderRows(rows);
  } catch {
    tbody.innerHTML = '<tr><td colspan="5" class="py-10 text-center text-on-surface-variant">Failed to load.</td></tr>';
  }
}

function renderRows(rows) {
  if (!tbody) return;
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="py-10 text-center text-on-surface-variant">No players yet.</td></tr>';
    return;
  }

  tbody.innerHTML = rows.map((u) => {
    const rankCell = rankBadge(u.rank);
    const accuracy = u.accuracy > 0
      ? `<span class="inline-flex items-center px-3 py-1 rounded-full bg-tertiary/10 text-tertiary border border-tertiary/20 text-sm font-bold">${u.accuracy}%</span>`
      : `<span class="text-on-surface-variant text-sm">—</span>`;
    const youLabel = u.is_me ? '<span class="text-secondary text-xs font-label ml-1">(you)</span>' : '';
    const rowClass = u.is_me ? 'ring-1 ring-inset ring-secondary/40' : '';
    const trendIcon = u.rank <= 3 ? 'trending_up' : (u.rank % 2 === 0 ? 'remove' : 'trending_down');
    const trendClass = u.rank <= 3 ? 'text-tertiary' : (u.rank % 2 === 0 ? 'text-on-surface-variant/50' : 'text-error');

    return `
      <tr class="hover:bg-white/5 transition-colors ${rowClass}">
        <td class="py-5 px-8">${rankCell}</td>
        <td class="py-5 px-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center font-headline font-bold ${u.is_me ? 'text-secondary border border-secondary/30' : 'text-primary'}">
              ${u.username[0].toUpperCase()}
            </div>
            <span class="font-headline font-medium text-lg">${u.username.toUpperCase()}${youLabel}</span>
          </div>
        </td>
        <td class="py-5 px-4 text-center">
          <span class="font-headline font-bold text-primary">${u.xp.toLocaleString()}</span>
        </td>
        <td class="py-5 px-4 text-center">${accuracy}</td>
        <td class="py-5 px-4 text-center text-on-surface-variant font-label">${u.segments.toLocaleString()}</td>
        <td class="py-5 px-8 text-right">
          <span class="material-symbols-outlined ${trendClass}">${trendIcon}</span>
        </td>
      </tr>`;
  }).join('');
}

function rankBadge(rank) {
  const medals = [
    { color: 'bg-yellow-500/10 text-yellow-400' },
    { color: 'bg-slate-300/10 text-slate-300' },
    { color: 'bg-orange-700/10 text-orange-500' },
  ];
  if (rank <= 3) {
    const m = medals[rank - 1];
    return `<div class="w-10 h-10 rounded-lg ${m.color} flex items-center justify-center">
              <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1;">military_tech</span>
            </div>`;
  }
  return `<span class="font-headline font-bold text-on-surface-variant pl-2">${rank}</span>`;
}
