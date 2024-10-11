const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d')
const resultElement = document.getElementById("predictinalResult"); // 予測結果を表示する要素
const clear = document.getElementById("clear");

const problemElement = document.getElementById("problem");
const answerElement = document.getElementById("answer");

//ランキング用
const submitScoreButton = document.getElementById("submitScore");
const usernameInput = document.getElementById("username");
const rankingsList = document.getElementById("rankings");
//
 
canvas.width = 640;  // ピクセルサイズを640pxに設定
canvas.height = 480; // ピクセルサイズを480pxに設定


// WebSocket接続の設定
const socket = io.connect('http://127.0.0.1:5000');  // 127.0.0.1 に接続する場合


// カウントダウン画像のパス
const countdownImages = [
    "/static/rogo/3.png",  // 3秒
    "/static/rogo/2.png",  // 2秒
    "/static/rogo/1.png"   // 1秒
];

let x = 0;
let y = 0;
let isDrawing = false;
let predictionData = null; // グローバル変数を定義
let problem_ans = null; // グローバル変数を定義

let score = 0;

//タイマー機能
let timeLeft = 10;
let timerElement = document.getElementById('timer');
let timerRunning = false;
let timeout = null;
////

document.addEventListener("keydown", (e)=>{
    if(e.key === "Enter" && !timerRunning){
        startCountdown();
    }
})

// カウントダウンを表示
function startCountdown() {
    let countdownIndex = 0;
    timerElement.textContent = '';  // カウントダウン時はタイマーのテキストを隠す

    function showNextImage() {
        if (countdownIndex < countdownImages.length) {
            const image = new Image();
            image.src = countdownImages[countdownIndex];
            image.onload = function() {
                clear_canvas();  // キャンバスをクリア
                ctx.drawImage(image, (canvas.width - image.width) / 2, (canvas.height - image.height) / 2);  // 画像をキャンバスの中央に表示
            };
            countdownIndex++;
            setTimeout(showNextImage, 1000);  // 1秒ごとに次の画像を表示
        } else {
            startGame();  // カウントダウン終了後にゲーム開始
        }
    }
    showNextImage();
}



// ゲーム開始、タイマー開始
function startGame() {
    timeLeft = 10;  // タイマーを10秒に設定
    timerElement.textContent = `残り時間: ${timeLeft}秒`;  // 初期の残り時間を表示
    timerRunning = true;  // タイマーが動作していることを示す
    clear_canvas();  // キャンバスをクリア
    enableDrawing();
    startTimer();  // タイマーを開始
    getProblem();
}

function startTimer(){
    timeout = setInterval(() => {
        timeLeft--;
        timerElement.textContent = `残り時間: ${timeLeft}秒`;

        if (timeLeft <= 0) {
            clearInterval(timeout);
            timerRunning = false;  // タイマーが終了
            disableDrawing();
            timerElement.textContent = "時間切れ！";
            alert("時間切れです。");
        }
    },1000); //1秒ごとに減らす
}

// 描画を有効化
function enableDrawing() {
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener("mouseout", stopDrawing_out);
    canvas.addEventListener("mousemove", draw);
}

function disableDrawing(){
    canvas.removeEventListener('mousedown', startDrawing);
    canvas.removeEventListener('mouseup', stopDrawing);
    canvas.removeEventListener("mouseout", stopDrawing_out);
    canvas.removeEventListener("mousemove", draw);
}



function startDrawing(e){
    isDrawing = true;
    x = e.offsetX;
    y = e.offsetY;
}

async function stopDrawing_out(){
    isDrawing = false;
}

async function stopDrawing(){
    isDrawing = false;
    ctx.beginPath();
    sendCanvasImage();
}

function draw(e){
    if (!isDrawing) return;
    ctx.beginPath();
    ctx.lineWidth = 30; //
    ctx.lineCap = "round";
    ctx.moveTo(x,y);
    x = e.offsetX;
    y = e.offsetY;
    ctx.lineTo(x,y);
    ctx.stroke();
}

// キャンバスの画像をBase64に変換してサーバーに送信
function sendCanvasImage() {
    const imageData = canvas.toDataURL("image/png");  // キャンバスの画像をBase64に変換
    socket.emit('predict_image', { image: imageData });  // サーバーに送信
}

// サーバーから予測結果を受け取る
socket.on('prediction_response', function(data) {
    if (data.message) {
        console.log(data.message);
        resultElement.textContent = data.message;  // エラーメッセージを表示
    } else {
        predictionData = data.prediction;
        console.log('予測結果:', data.prediction);
        resultElement.textContent = `予測結果: ${data.prediction}`;  // 予測結果を表示
        if (predictionData == problem_ans){
            getProblem();
            clear_canvas();
            score++;
        }
    }
});

// ランダムな問題をサーバーから取得
function getProblem() {
    socket.emit('generate_problem');  // サーバーに問題生成をリクエスト
}

// サーバーから問題と答えを受け取る
socket.on('problem_response', function(data) {
    console.log('問題:', data.problem);
    console.log('答え:', data.answer);
    problem_ans = data.answer;
    problemElement.textContent = `問題: ${data.problem}`;  // 問題文を表示
    answerElement.textContent = `答え: ${data.answer}`;    // 答えを表示
});

// スコアをサーバーに送信
function submitScore() {
    const username = usernameInput.value;
    if(!username){
        alert("ユーザ名を入力してください!")
        return;
    }
    socket.emit('submit_score', { username: username, score: score });  // サーバーにスコアを送信
    score = 0;
}

// スコア送信の結果を受け取る
socket.on('score_response', function(data) {
    console.log(data.message);
    alert(data.message);  // スコア送信の結果をアラートで表示
    getRankings();// 非同期処理をしているせいで、即時反映ができていない。
});

// ランキングを取得するリクエスト
function getRankings() {
    socket.emit('get_rankings');  // サーバーにランキング取得をリクエスト
}

// サーバーからランキング結果を受け取る
socket.on('rankings_response', function(rankings) {
    console.log('ランキング:', rankings);
    rankingsList.innerHTML = '';  // ランキングリストをクリア
    rankings.forEach((ranking, index) => {
        const listItem = document.createElement('li');
        listItem.textContent = `${index + 1}. ${ranking.username} - ${ranking.score}点`;
        rankingsList.appendChild(listItem);  // ランキングをリストに表示
    });
});


function clear_canvas(){
    ctx.clearRect(0, 0, canvas.width, canvas.height); // キャンバス全体をクリア
}
function checkAnswer() {
    const correctAnswer = parseInt(answer.textContent.split(": ")[1]);  // サーバーから受け取った答え
    const userPrediction = parseInt(resultElement.textContent.split(": ")[1]);  // 予測結果
    if (correctAnswer === userPrediction) {
        alert("正解です！");
    } else {
        alert(`不正解です。正解は ${correctAnswer} でした。`);
    }
}



clear.addEventListener("click",clear_canvas);

// イベントリスナーを追加
submitScoreButton.addEventListener("click", submitScore);
// 初回にランキングをロード
getRankings();
