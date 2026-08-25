import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="스트림잇 벽돌깨기 게임", page_icon="🎮", layout="centered")

st.title("🧱 파워업 벽돌깨기 (Breakout)")
st.caption("키보드 **좌/우 화살표키(또는 A/D)**로 이동하고, 레이저 아이템 획득 시 **스페이스바**로 사격하세요!")

# HTML5/JavaScript Canvas 기반 게임 코드
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background-color: #0e1117;
            color: #ffffff;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        canvas {
            border: 3px solid #FF4B4B;
            border-radius: 8px;
            background: #161b22;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        .info {
            margin-top: 10px;
            font-size: 14px;
            color: #8b949e;
        }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="600" height="500"></canvas>
<div class="info">아이템: 🔵 공 분할 | 🟢 패들 확장 | 🔴 레이저 파워업 | 🟧 관통볼 | ❤️ 목숨 +1</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// 게임 상태 변수
let score = 0;
let lives = 3;
let gameOver = false;
let gameWon = false;

// 패들 설정
const paddleHeight = 12;
let paddleWidth = 90;
let paddleX = (canvas.width - paddleWidth) / 2;
let rightPressed = false;
let leftPressed = false;
let spacePressed = false;
let hasLaser = false;
let laserTimer = 0;

// 공 설정 (다중 공 지원)
let balls = [
    { x: canvas.width / 2, y: canvas.height - 30, dx: 4, dy: -4, radius: 7, isFireball: false, fireTimer: 0 }
];

// 총알 (레이저)
let bullets = [];

// 벽돌 설정
const brickRowCount = 5;
const brickColumnCount = 8;
const brickWidth = 63;
const brickHeight = 20;
const brickPadding = 8;
const brickOffsetTop = 40;
const brickOffsetLeft = 18;

// 아이템 목록
let items = [];
const ITEM_TYPES = {
    MULTIBALL: { color: "#3182ce", text: "3xB", type: "MULTIBALL" },
    EXPAND: { color: "#38a169", text: "PAD", type: "EXPAND" },
    LASER: { color: "#e53e3e", text: "GUN", type: "LASER" },
    FIREBALL: { color: "#dd6b20", text: "FIRE", type: "FIREBALL" },
    LIFE: { color: "#d53f8c", text: "+1L", type: "LIFE" }
};

// 벽돌 초기화
const bricks = [];
const brickColors = ["#e53e3e", "#dd6b20", "#d69e2e", "#38a169", "#3182ce"];
for (let c = 0; c < brickColumnCount; c++) {
    bricks[c] = [];
    for (let r = 0; r < brickRowCount; r++) {
        // 20% 확률로 아이템을 품은 벽돌 생성
        let itemType = null;
        if (Math.random() < 0.35) {
            const keys = Object.keys(ITEM_TYPES);
            itemType = ITEM_TYPES[keys[Math.floor(Math.random() * keys.length)]];
        }
        bricks[c][r] = { x: 0, y: 0, status: 1, color: brickColors[r], item: itemType };
    }
}

// 키 이벤트 리스너
document.addEventListener("keydown", keyDownHandler, false);
document.addEventListener("keyup", keyUpHandler, false);

function keyDownHandler(e) {
    if (e.key === "Right" || e.key === "ArrowRight" || e.key === "d" || e.key === "D") rightPressed = true;
    else if (e.key === "Left" || e.key === "ArrowLeft" || e.key === "a" || e.key === "A") leftPressed = true;
    else if (e.key === " " || e.code === "Space") {
        if (hasLaser && !spacePressed) {
            bullets.push({ x: paddleX + 10, y: canvas.height - paddleHeight - 5 });
            bullets.push({ x: paddleX + paddleWidth - 10, y: canvas.height - paddleHeight - 5 });
        }
        spacePressed = true;
    }
}

function keyUpHandler(e) {
    if (e.key === "Right" || e.key === "ArrowRight" || e.key === "d" || e.key === "D") rightPressed = false;
    else if (e.key === "Left" || e.key === "ArrowLeft" || e.key === "a" || e.key === "A") leftPressed = false;
    else if (e.key === " " || e.code === "Space") spacePressed = false;
}

// 충돌 감지
function collisionDetection() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            const b = bricks[c][r];
            if (b.status === 1) {
                // 공과 벽돌 충돌
                balls.forEach(ball => {
                    if (ball.x > b.x && ball.x < b.x + brickWidth && ball.y > b.y && ball.y < b.y + brickHeight) {
                        if (!ball.isFireball) {
                            ball.dy = -ball.dy;
                        }
                        b.status = 0;
                        score += 10;
                        
                        // 아이템 드롭
                        if (b.item) {
                            items.push({ x: b.x + brickWidth/2, y: b.y, type: b.item, dy: 2 });
                        }
                    }
                });

                // 총알과 벽돌 충돌
                bullets.forEach((bullet, index) => {
                    if (bullet.x > b.x && bullet.x < b.x + brickWidth && bullet.y > b.y && bullet.y < b.y + brickHeight) {
                        b.status = 0;
                        score += 10;
                        bullets.splice(index, 1);
                        if (b.item) {
                            items.push({ x: b.x + brickWidth/2, y: b.y, type: b.item, dy: 2 });
                        }
                    }
                });
            }
        }
    }
}

// 그려주기 함수들
function drawBalls() {
    balls.forEach(ball => {
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        ctx.fillStyle = ball.isFireball ? "#ff4500" : "#ffffff";
        ctx.shadowBlur = ball.isFireball ? 12 : 0;
        ctx.shadowColor = "#ff4500";
        ctx.fill();
        ctx.closePath();
        ctx.shadowBlur = 0; // 초기화
    });
}

function drawPaddle() {
    ctx.beginPath();
    ctx.rect(paddleX, canvas.height - paddleHeight, paddleWidth, paddleHeight);
    ctx.fillStyle = hasLaser ? "#e53e3e" : "#0095DD";
    ctx.fill();
    ctx.closePath();
}

function drawBricks() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            if (bricks[c][r].status === 1) {
                const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
                const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
                bricks[c][r].x = brickX;
                bricks[c][r].y = brickY;
                ctx.beginPath();
                ctx.rect(brickX, brickY, brickWidth, brickHeight);
                ctx.fillStyle = bricks[c][r].color;
                ctx.fill();
                
                // 아이템 아이콘 살짝 표시
                if (bricks[c][r].item) {
                    ctx.fillStyle = "rgba(255,255,255,0.4)";
                    ctx.font = "bold 10px Arial";
                    ctx.fillText("★", brickX + brickWidth/2 - 4, brickY + 14);
                }
                ctx.closePath();
            }
        }
    }
}

function drawItems() {
    items.forEach((item, index) => {
        item.y += item.dy;
        ctx.beginPath();
        ctx.arc(item.x, item.y, 10, 0, Math.PI * 2);
        ctx.fillStyle = item.type.color;
        ctx.fill();
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 9px Arial";
        ctx.textAlign = "center";
        ctx.fillText(item.type.text, item.x, item.y + 3);
        ctx.closePath();

        // 패들과 아이템 충돌 (아이템 획득)
        if (item.y + 10 >= canvas.height - paddleHeight &&
            item.x >= paddleX && item.x <= paddleX + paddleWidth) {
            
            applyItem(item.type);
            items.splice(index, 1);
        } else if (item.y > canvas.height) {
            items.splice(index, 1);
        }
    });
}

function applyItem(itemType) {
    if (itemType.type === "MULTIBALL") {
        let currentCount = balls.length;
        for (let i = 0; i < 2; i++) {
            if (balls.length < 9) {
                let baseBall = balls[0] || { x: canvas.width / 2, y: canvas.height - 30 };
                balls.push({
                    x: baseBall.x,
                    y: baseBall.y,
                    dx: (Math.random() - 0.5) * 8,
                    dy: -4,
                    radius: 7,
                    isFireball: false
                });
            }
        }
    } else if (itemType.type === "EXPAND") {
        paddleWidth = 140;
        setTimeout(() => { paddleWidth = 90; }, 8000); // 8초 후 원복
    } else if (itemType.type === "LASER") {
        hasLaser = true;
        laserTimer = 300; // 프레임 단위 타이머
    } else if (itemType.type === "FIREBALL") {
        balls.forEach(b => {
            b.isFireball = true;
            setTimeout(() => { b.isFireball = false; }, 6000); // 6초 유지
        });
    } else if (itemType.type === "LIFE") {
        lives++;
    }
}

function drawBullets() {
    ctx.fillStyle = "#ff0000";
    bullets.forEach((bullet, index) => {
        bullet.y -= 7;
        ctx.fillRect(bullet.x - 2, bullet.y, 4, 10);
        if (bullet.y < 0) bullets.splice(index, 1);
    });
}

function drawUI() {
    ctx.font = "16px Arial";
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "left";
    ctx.fillText(`점수: ${score}`, 15, 25);
    ctx.fillText(`목숨: ${'❤️'.repeat(lives)}`, canvas.width - 120, 25);
}

function update() {
    if (gameOver || gameWon) return;

    // 패들 이동
    if (rightPressed && paddleX < canvas.width - paddleWidth) paddleX += 7;
    else if (leftPressed && paddleX > 0) paddleX -= 7;

    // 레이저 타이머 관리
    if (hasLaser) {
        laserTimer--;
        if (laserTimer <= 0) hasLaser = false;
    }

    // 공 위치 업데이트 및 벽 충돌 처리
    balls.forEach((ball, index) => {
        ball.x += ball.dx;
        ball.y += ball.dy;

        // 좌우 벽 충돌
        if (ball.x + ball.dx > canvas.width - ball.radius || ball.x + ball.dx < ball.radius) {
            ball.dx = -ball.dx;
        }
        // 천장 충돌
        if (ball.y + ball.dy < ball.radius) {
            ball.dy = -ball.dy;
        }
        // 패들 충돌
        else if (ball.y + ball.dy > canvas.height - ball.radius - paddleHeight) {
            if (ball.x > paddleX && ball.x < paddleX + paddleWidth) {
                // 패들의 부딪힌 위치에 따라 반사 각도 조절
                let hitPoint = (ball.x - (paddleX + paddleWidth / 2)) / (paddleWidth / 2);
                ball.dx = hitPoint * 5;
                ball.dy = -Math.abs(ball.dy);
            } else if (ball.y > canvas.height) {
                // 바닥으로 떨어진 공 제거
                balls.splice(index, 1);
            }
        }
    });

    // 모든 공을 놓쳤을 때
    if (balls.length === 0) {
        lives--;
        if (lives <= 0) {
            gameOver = true;
        } else {
            // 공 다시 생성
            balls.push({ x: canvas.width / 2, y: canvas.height - 30, dx: 4, dy: -4, radius: 7, isFireball: false });
            paddleX = (canvas.width - paddleWidth) / 2;
        }
    }

    // 승리 조건 체크
    let allCleared = true;
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            if (bricks[c][r].status === 1) allCleared = false;
        }
    }
    if (allCleared) gameWon = true;

    collisionDetection();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawBricks();
    drawBalls();
    drawPaddle();
    drawItems();
    drawBullets();
    drawUI();

    if (gameOver) {
        ctx.font = "36px Arial";
        ctx.fillStyle = "#ff4b4b";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2);
        return;
    }
    if (gameWon) {
        ctx.font = "36px Arial";
        ctx.fillStyle = "#00ffcc";
        ctx.textAlign = "center";
        ctx.fillText("VICTORY!", canvas.width / 2, canvas.height / 2);
        return;
    }

    update();
    requestAnimationFrame(draw);
}

draw();
</script>
</body>
</html>
"""

# Streamlit에 HTML 렌더링
components.html(game_code, height=580)
