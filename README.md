# Mini Metro Simulator — 実行手順

このプロジェクトは Docker で動かす想定です。**出力ファイルをホスト側に保存**できるよう、`/app/out` をマウントして実行します。以下をそのままコピペで使えます。

---

## 前提

* Docker がインストール済み
* プロジェクト直下に `Dockerfile` と `main.py` 等のコードがある

---

## ビルド

```bash
docker build -t mm-sim .
```

---

## 実行（出力をホストへ永続化）

> ホストの `./out` に結果が保存されます（例：`./out/run_0/`）。

```bash
mkdir -p out
docker run --rm \
  -v "$PWD/out":/app/out \
  -e OUTPUT_DIR=/app/out \
  mm-sim
```

### Windows PowerShell の場合

```powershell
mkdir out -ea 0
docker run --rm `
  -v "${PWD}\out:/app/out" `
  -e OUTPUT_DIR=/app/out `
  mm-sim
```

---

## 実行後の出力例

```bash
ls -R out
# out/
# └── run_0/
#     ├── log.json        # ログ（あなたの Logger 実装に依存）
#     └── そのほか出力...
```

再実行すると `run_1/`, `run_2/` … と連番で作成されます。

---

## よくある質問（FAQ）

### Q. 出力が見当たりません

* コンテナ内でだけ作成され、ホストに残っていない可能性があります。必ず `-v "$PWD/out":/app/out` を付けて実行してください。
* `main.py` 側が `OUTPUT_DIR` を見ているか確認してください（例）：

  ```python
  base_output = Path(os.environ.get("OUTPUT_DIR", "./outputs"))
  ```

### Q. 権限エラーが出ます

* まずは `out` フォルダを作ってから実行してください：`mkdir -p out`
* WSL/共有ドライブ環境では、`-u $(id -u):$(id -g)` を付けると改善することがあります（Linux/macOS）：

  ```bash
  docker run --rm \
    -u $(id -u):$(id -g) \
    -v "$PWD/out":/app/out \
    -e OUTPUT_DIR=/app/out \
    mm-sim
  ```

---

## コンテナに入って中身を確認したい

```bash
# バックグラウンドで起動
docker run -d --name mm1 \
  -v "$PWD/out":/app/out \
  -e OUTPUT_DIR=/app/out \
  mm-sim

# 中に入って確認
docker exec -it mm1 bash
ls -R /app/out

# 後片付け
docker rm -f mm1
```

---

## クリーンアップ

```bash
# コンテナ（停止中）削除
docker container prune -f

# イメージ削除
docker rmi mm-sim
```

---

## ローカル実行（Docker を使わない場合）

> 依存は `requirements.txt` を参照。仮想環境は任意。

```bash
python -m pip install -r requirements.txt

# 出力先（例：./out）を環境変数で指定して実行
export OUTPUT_DIR=./out
python main.py
```

Windows（PowerShell）:

```powershell
python -m pip install -r requirements.txt
$env:OUTPUT_DIR = ".\out"
python .\main.py
```

---

必要に応じて、可視化や追加オプションの実行方法を追記してください（スクリプト側で CLI 引数や環境変数を受け取る実装にしておくと便利です）。
