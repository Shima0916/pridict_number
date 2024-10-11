# Flask Webアプリケーション（TensorFlow、WebSocket、MySQL使用）

このアプリは、FlaskをベースとしたWebアプリケーションで、TensorFlowを使用して画像(キャンバスの内容)の予測を行い、Flask-SocketIOを使用してリアルタイムのWebSocket通信をしています。また、MySQLをバックエンドデータベースとして使用し、スコアとランキングを保存しています。
ユーザはキャンバス上に数字を描き、その数字を予測モデルに送信して結果を受け取ることができます。

## 機能

- リアルタイム画像予測（TensorFlowとWebSocketを使用）
- スコア提出およびランキングシステム（MySQLを使用）
- キャンバスを使ったインタラクティブなユーザーインターフェース

## 必要な環境

このプロジェクトを実行するには、以下のソフトウェアがインストールされている必要があります。

- Python 3.12.6
- MySQL
- Flask
- Flask-SocketIO
- TensorFlow
- MySQL Connector（Python用）
- OpenCV
- PIL (Pillow)

## セットアップ手順

1. **リポジトリをクローン**

    以下のコマンドを実行して、プロジェクトをローカル環境にクローンします。

   ```bash
   git clone https://github.com/Shima0916/pridict_number.git
   cd your-project-directory
   ```
2. **リポジトリをクローン**

    仮想環境を作成してもよい(任意)
   ```bash
   git clone https://github.com/Shima0916/pridict_number.git
   cd your-project-directory
   ```
    その後、必要なPythonパッケージを pip でインストールしてください。
    ```bash
    pip install -r requirements.txt
    ```
3. **MySQLデータベースの設定**

    MySQLで新しいデータベースを作成してください。

    ```sql
    CREATE DATABASE ranking_db;
    ```

    app.py 内のデータベース設定 (mysql_config) を自分の環境に合わせて変更してください。

    ```python
    mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your-password',
    'database': 'ranking_db'
    }
    ```

    rankings テーブルを作成してください。
    ```sql
    CREATE TABLE rankings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    score INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ```
4. **アプリケーションの実行**

    ```bash
    python app.py
    ```
5. **アクセス**

    Webブラウザで http://127.0.0.1:5000 にアクセスしてアプリケーションを確認できます。

## ファイル構成
<pre>
.
├── README.md
├── app.py
├── model
│   ├── my_model1.h5
│   ├── my_model10.h5
│   ├── my_model2.h5
│   ├── my_model20.h5
│   ├── my_model20_upgrade.h5
│   ├── my_model3.h5
│   └── my_model4.h5
├── predict
│   └── create_model_upgrade.py
├── requirements.txt
├── static
│   ├── rogo
│   │   ├── 1.png
│   │   ├── 2.png
│   │   └── 3.png
│   ├── script.js
│   └── style.css
└── templates  
        └── index.html

</pre>