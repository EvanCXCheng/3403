'use strict';

// ── Stage ──────────────────────────────────────────────────────────────────────
const viewport = document.getElementById('konva-container');

const stage = new Konva.Stage({
  container: 'konva-container',
  width:  viewport.clientWidth,
  height: viewport.clientHeight,
});

const imageLayer = new Konva.Layer();
const drawLayer  = new Konva.Layer();
stage.add(imageLayer);
stage.add(drawLayer);

// ── Load scan image ────────────────────────────────────────────────────────────
// imgBase records the object-contain layout at scale=1; used for mask export.
let imgBase = { x: 0, y: 0, width: 1, height: 1 };

const scanEl = new window.Image();
scanEl.onload = () => {
  const sw    = stage.width();
  const sh    = stage.height();
  const scale = Math.min(sw / scanEl.width, sh / scanEl.height);
  const w     = scanEl.width  * scale;
  const h     = scanEl.height * scale;
  imgBase     = { x: (sw - w) / 2, y: (sh - h) / 2, width: w, height: h };

  imageLayer.add(new Konva.Image({
    image: scanEl, ...imgBase, opacity: 0.85,
  }));
  imageLayer.batchDraw();
};
scanEl.src = SCAN_IMAGE_URL;

// ── Tool state ─────────────────────────────────────────────────────────────────
let activeTool  = 'brush';
let isDrawing   = false;
let currentLine = null;
let strokeCount = 0;
let startTime   = null;
const BRUSH_PX  = 18;

// ── Tool selection (brush / eraser / pan) ─────────────────────────────────────
const toolBtns = [
  document.getElementById('tool-brush'),
  document.getElementById('tool-eraser'),
  document.getElementById('tool-pan'),
];

function activateTool(toolId) {
  activeTool = toolId;
  toolBtns.forEach((b) => {
    const active = b.id === 'tool-' + toolId;
    b.classList.toggle('bg-cyan-400',  active);
    b.classList.toggle('text-gray-950', active);
    b.classList.toggle('bg-gray-800',  !active);
    b.classList.toggle('text-gray-400', !active);
  });
  stage.draggable(toolId === 'pan');
  stage.container().style.cursor = toolId === 'pan' ? 'grab' : 'crosshair';
}

toolBtns.forEach((b) =>
  b.addEventListener('click', () => activateTool(b.id.replace('tool-', '')))
);

// ── Drawing ────────────────────────────────────────────────────────────────────
stage.on('mousedown touchstart', () => {
  if (activeTool !== 'brush' && activeTool !== 'eraser') return;
  isDrawing = true;
  if (!startTime) startTime = Date.now();

  const pos = stage.getRelativePointerPosition();
  currentLine = new Konva.Line({
    points:    [pos.x, pos.y],
    stroke:    activeTool === 'eraser' ? 'black' : 'rgba(60, 215, 255, 0.55)',
    strokeWidth: BRUSH_PX / stage.scaleX(),   // constant screen size regardless of zoom
    lineCap:   'round',
    lineJoin:  'round',
    tension:   0.4,
    globalCompositeOperation:
      activeTool === 'eraser' ? 'destination-out' : 'source-over',
  });
  drawLayer.add(currentLine);
});

stage.on('mousemove touchmove', () => {
  if (!isDrawing || !currentLine) return;
  const pos = stage.getRelativePointerPosition();
  currentLine.points(currentLine.points().concat([pos.x, pos.y]));
  drawLayer.batchDraw();
});

stage.on('mouseup touchend', () => {
  if (isDrawing && currentLine) strokeCount++;
  isDrawing   = false;
  currentLine = null;
  updateProgress();
});

// Switch cursor back to crosshair after a pan drag ends
stage.on('dragend', () => {
  stage.container().style.cursor = 'grab';
});

// ── Scroll-wheel zoom (cursor-centred) ────────────────────────────────────────
stage.container().addEventListener('wheel', (e) => {
  e.preventDefault();
  const oldScale = stage.scaleX();
  const pointer  = stage.getPointerPosition();
  const origin   = {
    x: (pointer.x - stage.x()) / oldScale,
    y: (pointer.y - stage.y()) / oldScale,
  };
  const newScale = Math.min(Math.max(oldScale * (e.deltaY < 0 ? 1.1 : 0.9), 0.3), 10);
  stage.scale({ x: newScale, y: newScale });
  stage.position({
    x: pointer.x - origin.x * newScale,
    y: pointer.y - origin.y * newScale,
  });
  stage.batchDraw();
}, { passive: false });

// ── Reset zoom ─────────────────────────────────────────────────────────────────
document.getElementById('tool-zoom').addEventListener('click', () => {
  stage.scale({ x: 1, y: 1 });
  stage.position({ x: 0, y: 0 });
  stage.batchDraw();
  activateTool('brush');
});

// ── Undo (per-stroke, not clear-all) ─────────────────────────────────────────
document.getElementById('tool-undo').addEventListener('click', () => {
  const children = drawLayer.getChildren();
  if (!children.length) return;
  children[children.length - 1].destroy();
  drawLayer.batchDraw();
  strokeCount = Math.max(0, strokeCount - 1);
  updateProgress();
});

// ── Progress ───────────────────────────────────────────────────────────────────
function updateProgress() {
  const pct = Math.min(strokeCount * 5, 100);
  document.getElementById('progress-bar').style.width = pct + '%';
  document.getElementById('progress-pct').textContent = pct + '%';
  document.getElementById('dice-score').textContent   = pct > 0 ? pct + '%' : '—';
}

// ── Resize ─────────────────────────────────────────────────────────────────────
window.addEventListener('resize', () => {
  stage.width(viewport.clientWidth);
  stage.height(viewport.clientHeight);
  stage.batchDraw();
});

// ── Results modal ──────────────────────────────────────────────────────────────
function showModal(accuracyPct, xpAwarded, overallPct) {
  document.getElementById('modal-accuracy').textContent = accuracyPct;
  document.getElementById('modal-xp').textContent       = '+' + xpAwarded;
  document.getElementById('modal-overall').textContent  = overallPct + '%';
  document.getElementById('results-modal').classList.remove('hidden');
}

document.getElementById('modal-next').addEventListener('click', () => {
  window.location.href = '/segmentation';
});

// ── Submit ─────────────────────────────────────────────────────────────────────
document.getElementById('btn-submit').addEventListener('click', async () => {
  if (strokeCount === 0) {
    alert('Please draw at least one annotation before submitting.');
    return;
  }

  // Export the annotation mask in the base coordinate space (scale=1, no pan)
  // so the pixel layout is always consistent regardless of current zoom/pan.
  const savedScale = stage.scaleX();
  const savedPos   = stage.position();
  stage.scale({ x: 1, y: 1 });
  stage.position({ x: 0, y: 0 });
  imageLayer.hide();
  const maskDataUrl = stage.toDataURL({ mimeType: 'image/png', pixelRatio: 1 });
  imageLayer.show();
  stage.scale({ x: savedScale, y: savedScale });
  stage.position(savedPos);
  stage.batchDraw();

  const btnSubmit = document.getElementById('btn-submit');
  btnSubmit.disabled    = true;
  btnSubmit.textContent = 'Submitting…';

  try {
    const resp = await fetch(SUBMIT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
      body: JSON.stringify({
        image_id:      IMAGE_ID,
        mask:          maskDataUrl,
        img_offset_x:  imgBase.x,
        img_offset_y:  imgBase.y,
        img_display_w: imgBase.width,
        img_display_h: imgBase.height,
      }),
    });

    const result = await resp.json();
    if (result.ok) {
      const accuracyPct = (result.dice_score * 100).toFixed(1) + '%';
      document.getElementById('dice-score').textContent   = accuracyPct;
      document.getElementById('progress-pct').textContent = '100%';
      document.getElementById('progress-bar').style.width = '100%';
      showModal(accuracyPct, result.xp_awarded, result.accuracy_pct);
    } else {
      alert('Submission failed: ' + (result.error || 'Unknown error'));
    }
  } catch (err) {
    alert('Network error — please try again.');
    console.error(err);
  } finally {
    btnSubmit.disabled    = false;
    btnSubmit.textContent = '✓ Submit Analysis';
  }
});
