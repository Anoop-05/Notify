const canvas = document.getElementById("snowCanvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let snowflakes = [];

for (let i = 0; i < 100; i++) {
    snowflakes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 4 + 1,
        d: Math.random() * 2 + 1
    });
}

function drawSnow() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "white";
    ctx.beginPath();

    for (let i = 0; i < snowflakes.length; i++) {
        let sf = snowflakes[i];
        ctx.moveTo(sf.x, sf.y);
        ctx.arc(sf.x, sf.y, sf.r, 0, Math.PI * 2);
    }
    ctx.fill();
    updateSnow();
}

function updateSnow() {
    for (let i = 0; i < snowflakes.length; i++) {
        let sf = snowflakes[i];
        sf.y += sf.d;

        if (sf.y > canvas.height) {
            sf.y = 0;
            sf.x = Math.random() * canvas.width;
        }
    }
}

function animateSnow() {
    drawSnow();
    requestAnimationFrame(animateSnow);
}

animateSnow();
