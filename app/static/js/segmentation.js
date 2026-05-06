'use strict';

// Tool state
let activeTool = 'brush';
let isDrawing = false;
let startTime = null;
let strokeCount = 0;

const canvas = document.getElementById('seg-canvas');
const ctx = canvas.getContext('2d');

// Size canvas to match its container
function resizeCanvas() {
  const container = canvas.parentElement;
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Tool button selection
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

// Canvas drawing
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

  if (activeTool === 'eraser') {
    ctx.clearRect(e.offsetX - 10, e.offsetY - 10, 20, 20);
  } else {
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.strokeStyle = 'rgba(60, 215, 255, 0.7)';
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();
  }
});

canvas.addEventListener('mouseup', () => {
  if (isDrawing) strokeCount++;
  isDrawing = false;
  updateProgress();
});

canvas.addEventListener('mouseleave', () => { isDrawing = false; });

// Undo clears entire canvas (simple implementation)
document.getElementById('tool-undo').addEventListener('click', () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  strokeCount = 0;
  updateProgress();
});

// Progress grows with strokes drawn
function updateProgress() {
  const pct = Math.min(strokeCount * 5, 100);
  document.getElementById('progress-bar').style.width = pct + '%';
  document.getElementById('progress-pct').textContent = pct + '%';
  if (pct > 0) {
    const dice = (0.70 + pct / 1000).toFixed(2);
    document.getElementById('dice-score').textContent = dice;
  }
}

// Submit analysis
document.getElementById('btn-submit').addEventListener('click', () => {
  if (strokeCount === 0) {
    alert('Please draw at least one annotation before submitting.');
    return;
  }
  const timeSpent = startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;
  console.log('Submitting segmentation', { strokes: strokeCount, timeSpent });
  // AJAX submission will be wired in Step 6
});
