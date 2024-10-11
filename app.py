from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import tensorflow as tf
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import random
import cv2
import matplotlib
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
socketio = SocketIO(app)  # Flask-SocketIOの設定


# MySQLデータベース接続設定
mysql_config = {
    'host': 'localhost',  # データベースサーバのホスト名
    'user': 'root',       # MySQLユーザー名
    'database': 'ranking_db' # 使用するデータベース名
}

# モデルの読み込み
model = tf.keras.models.load_model('model/my_model20_upgrade.h5')

@app.route("/")
def index():
    return render_template("index.html")

# WebSocket用の画像予測エンドポイント
@socketio.on("predict_image")
def handle_predict_image(data):
    image_data = data.get("image")  # "image"というキーで送られたデータをとりだす

    if not image_data:
        emit('prediction_response', {'message': '画像データが不足しています。'})
        return
    
    image_data = image_data.split(",")[1]  # Base64データのヘッダー部分を除去
    image = Image.open(BytesIO(base64.b64decode(image_data)))

    # RGBA画像を処理する場合、透明な部分を白に置き換える
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])  # アルファチャンネルをマスクとして使う
        image = background.convert('L')  # グレースケールに変換

    # 画像をグレースケールに変換
    image = image.resize((28, 28))  # モデルの期待するサイズに合わせる
    image = np.array(image)
    # imgを白黒反転
    image = cv2.bitwise_not(image)
    image = image.astype('float32') / 255.0
    image = image.reshape(1, 28, 28, 1)

    predictions = model.predict(image)
    predicted_class = np.argmax(predictions)

    # # 画像を保存
    # matplotlib.use('Agg')  # GUIを使わずに処理
    # plt.imshow(image.squeeze(), cmap='gray')
    # plt.title("Inverted Image")
    # plt.axis("off")  # 軸を非表示
    # plt.savefig("static/inverted_image.png")  # 画像を保存

    # クライアントに予測結果を送信
    emit('prediction_response', {'prediction': int(predicted_class)})

# WebSocket用の問題生成エンドポイント
@socketio.on('generate_problem')
def generate_problems():
    operations = ['+', '-']
    num1 = random.randint(0, 4)
    num2 = random.randint(0, 4)
    operation = random.choice(operations)
    
    if operation == '-' and num1 < num2:
        num1, num2 = num2, num1  # num1がnum2以上になるようにする
    
    problem = f"{num1} {operation} {num2}"
    answer = eval(problem)
    
    # クライアントに問題と答えを送信
    emit('problem_response', {'problem': problem, 'answer': answer})


########################

# スコアを送信するエンドポイント
@socketio.on('submit_score')
def submit_score(data):
    username = data.get('username')
    score = data.get('score')
    
    if username and score is not None:
        try:
            # MySQLデータベースに接続
            connection = mysql.connector.connect(**mysql_config)
            cursor = connection.cursor()
            
            # スコアをデータベースに挿入
            insert_query = "INSERT INTO rankings (username, score) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, score))
            connection.commit()
            emit('score_response', {'message': 'スコアが送信されました。'})
        except Error as err:
            emit('score_response', {'message': f'エラーが発生しました: {err}'})
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return jsonify({'message': 'スコアが送信されました。'})
    else:
        emit('score_response', {'message': 'ユーザー名またはスコアが不足しています。'})

    
# WebSocket用のランキング取得エンドポイント
@socketio.on('get_rankings')
def get_rankings():
    try:
        # MySQLデータベースに接続
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor(dictionary=True)
        
        # スコアの高い順にランキングを取得
        select_query = "SELECT username, score FROM rankings ORDER BY score DESC LIMIT 10"
        cursor.execute(select_query)
        rankings = cursor.fetchall()
        # クライアントにランキングを送信
        emit('rankings_response', rankings)
    except Error as err:
        emit('rankings_response', {'message': f'エラーが発生しました: {err}'})
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    socketio.run(app, debug=True)