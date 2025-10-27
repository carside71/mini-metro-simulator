# ベースイメージ：軽量な Python 3.10
FROM python:3.10-slim

# 作業ディレクトリを作成
WORKDIR /app

# requirements.txt をコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# メインスクリプトを実行
CMD ["python", "main.py"]
# CMD ["python", "tsp.py"]
