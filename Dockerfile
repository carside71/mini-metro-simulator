# ベースイメージ：軽量な Python 3.10
FROM python:3.10-slim

# 作業ディレクトリを作成
WORKDIR /app

# requirements.txt をコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 出力用ディレクトリを作成（書き込み権限を確保）
RUN mkdir -p /app/out && chmod -R 777 /app/out

# デフォルトの実行コマンド
# 出力先を /app/out に変更して実行
CMD ["python", "main.py"]
