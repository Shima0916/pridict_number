import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# データ読み込み
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

# データの形状を修正
x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)

# 正規化
x_train = x_train.astype('float32') / 255.0
x_test = x_test.astype('float32') / 255.0

# One-hotエンコーディング
y_train = tf.keras.utils.to_categorical(y_train, num_classes=10)
y_test = tf.keras.utils.to_categorical(y_test, num_classes=10)

# 学習データを48,000枚とバリデーションデータを12,000枚に分割
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, random_state=42)

# ImageDataGeneratorによるデータ拡張
# ImageDataGenerator設定
datagen = ImageDataGenerator(
    featurewise_center=False,               # データセット全体の平均で正規化しない
    samplewise_center=False,                # 各サンプルごとに平均を0にしない
    featurewise_std_normalization=False,    # データセットの標準偏差で正規化しない
    samplewise_std_normalization=False,     # 各サンプルの標準偏差で正規化しない
    zca_whitening=False,                    # ZCA白色化なし
    rotation_range=50,                      # -50度から50度までランダム回転
    width_shift_range=0.3,                  # 横方向のスライド範囲30%
    height_shift_range=0.2,                 # 縦方向のスライド範囲20%
    zoom_range=[1.0, 1.5],                  # 拡大縮小範囲1.0〜1.5
    horizontal_flip=False,                  # 水平反転なし
    vertical_flip=False                     # 垂直反転なし
)


# モデルの作成
model = tf.keras.models.Sequential([
  tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(10, activation='softmax')
])

# モデルのコンパイル
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# データ拡張を適用してモデルに学習
model.fit(datagen.flow(x_train, y_train, batch_size=32),
          validation_data=(x_val, y_val),
          steps_per_epoch=len(x_train) // 32, epochs=20)

# モデルの評価
loss, accuracy = model.evaluate(x_test, y_test)
print('Test accuracy:', accuracy)

# モデルの保存
model.save("a.h5")
