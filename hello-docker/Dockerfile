# 軽量なPythonベースのイメージを使用します（Python 3.9のスリム版）
FROM python:3.9-slim

# 作業ディレクトリを設定します（コンテナ内での作業場所を指定）
WORKDIR /app

# アプリケーションコードをコンテナ内にコピーします（ローカルのapp/ディレクトリをコンテナ内にコピー）
COPY app/ .

# Pythonスクリプトを実行するコマンドを設定します（コンテナ起動時にmain.pyを実行）
CMD ["python", "main.py"]
