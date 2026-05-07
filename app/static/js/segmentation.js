'use strict';

// Tool state
let activeTool = 'brush';
let isDrawing = false;
let startTime = null;
let strokeCount = 0;
let brushSize = 18;

const canvas = document.getElementById('seg-canvas');
const ctx = canvas.getContext('2d');

// ── Canvas resize (preserves content) ─────────────────────────────────────────
function resizeCanvas() {
  const saved = canvas.toDataURL();
  const container = canvas.parentElement;
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
  const img = new Image();
  img.onload = () => ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  img.src = saved;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// ── Tool selection ─────────────────────────────────────────────────────────────
document.querySelectorAll('[id^="tool-"]').forEach((btn) => {
  btn.addEventListener('click', () => {
    activeTool = btn.id.replace('tool-', '');
    document.querySelectorAll('[id^="tool-"]').forEach((b) => {
      b.classList.remove('bg-cyan-400', 'text-gray-950');
      b.classList.add('bg-gray-800', 'text-gray-400');
    });
    btn.classList.remove('bg-gray-800', 'text-gray-400');
    btn.classList.add('bg-cyan-400', 'text-gray-950');
  });
});

// ── Drawing ────────────────────────────────────────────────────────────────────
canvas.addEventListener('mousedown', (e) => {
  if (activeTool !== 'brush' && activeTool !== 'eraser') return;
  isDrawing = true;
  if (!startTime) startTime = Date.now();
  ctx.beginPath();
  ctx.moveTo(e.offsetX, e.offsetY);
});

canvas.addEventListener('mousemove', (e) => {
  document.getElementById('coord-x').textContent = e.offsetX.toFixed(1);
  document.getElementById('coord-y').textContent = e.offsetY.toFixed(1);

  if (!isDrawing) return;

  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.lineWidth = brushSize;

  if (activeTool === 'eraser') {
    ctx.globalCompositeOperation = 'destination-out';
    ctx.strokeStyle = 'rgba(0,0,0,1)';
  } else {
    ctx.globalCompositeOperation = 'source-over';
    ctx.strokeStyle = 'rgba(60, 215, 255, 0.35)';
  }

  ctx.lineTo(e.offsetX, e.offsetY);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(e.offsetX, e.offsetY);
});

canvas.addEventListener('mouseup', () => {
  if (isDrawing) strokeCount++;
  isDrawing = false;
  ctx.beginPath(); // prevent strokes connecting on next mousedown
  updateProgress();
});

canvas.addEventListener('mouseleave', () => {
  isDrawing = false;
  ctx.beginPath();
});

// ── Undo ───────────────────────────────────────────────────────────────────────
document.getElementById('tool-undo').addEventListener('click', () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  strokeCount = 0;
  updateProgress();
});

// ── Progress ───────────────────────────────────────────────────────────────────
function updateProgress() {
  const pct = Math.min(strokeCount * 5, 100);
  document.getElementById('progress-bar').style.width = pct + '%';
  document.getElementById('progress-pct').textContent = pct + '%';
  if (pct > 0) {
    const dice = (0.70 + pct / 1000).toFixed(2);
    document.getElementById('dice-score').textContent = dice;
  }
}

// ── Submit ─────────────────────────────────────────────────────────────────────
document.getElementById('btn-submit').addEventListener('click', () => {
  if (strokeCount === 0) {
    alert('Please draw at least one annotation before submitting.');
    return;
  }
  const timeSpent = startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;
  const mask = canvas.toDataURL('image/png');
  console.log('Submitting segmentation', { strokes: strokeCount, timeSpent, mask });
  // AJAX submission to be wired in step 6
});