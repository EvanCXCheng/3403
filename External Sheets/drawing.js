const canvas = document.getElementById("drawCanvas");
const container = canvas.parentElement;
const ctx = canvas.getContext("2d");

const brushTool = document.getElementById("brush_tool");
const eraserTool = document.getElementById("eraser_tool");
const undoTool = document.getElementById("undo_tool");
const submitBtn = document.getElementById("submit_analysis");

let drawing = false;
let mode = "brush";
let brushSize = 18;

function resizeCanvas() {
const rect = container.getBoundingClientRect();
const saved = canvas.toDataURL();

canvas.width = rect.width;
canvas.height = rect.height;

const img = new Image();
img.onload = () => ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
img.src = saved;
}

function getPos(e) {
const rect = canvas.getBoundingClientRect();
return {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
};
}

function startDraw(e) {
drawing = true;
const pos = getPos(e);
ctx.beginPath();
ctx.moveTo(pos.x, pos.y);
}

function stopDraw() {
drawing = false;
ctx.beginPath();
}

function draw(e) {
if (!drawing) return;

const pos = getPos(e);

ctx.lineCap = "round";
ctx.lineJoin = "round";
ctx.lineWidth = brushSize;

if (mode === "eraser") {
    ctx.globalCompositeOperation = "destination-out";
    ctx.strokeStyle = "rgba(0,0,0,1)";
} else {
    ctx.globalCompositeOperation = "source-over";
    ctx.strokeStyle = "rgba(60, 215, 255, 0.35)";
}

ctx.lineTo(pos.x, pos.y);
ctx.stroke();
ctx.beginPath();
ctx.moveTo(pos.x, pos.y);
}

canvas.addEventListener("mousedown", startDraw);
canvas.addEventListener("mousemove", draw);
canvas.addEventListener("mouseup", stopDraw);
canvas.addEventListener("mouseleave", stopDraw);

brushTool.addEventListener("click", () => {
mode = "brush";
});

eraserTool.addEventListener("click", () => {
mode = "eraser";
});

undoTool.addEventListener("click", () => {
ctx.clearRect(0, 0, canvas.width, canvas.height);
});

submitBtn.addEventListener("click", () => {
const mask = canvas.toDataURL("image/png");
console.log("Exported mask:", mask);
});

window.addEventListener("resize", resizeCanvas);
resizeCanvas();