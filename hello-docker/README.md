# trading

## Dockerコンテナの実行方法

1. `docker-compose`を使用してDockerイメージをビルド:
   ```bash
   docker-compose build
   ```

2. `docker-compose`を使用してコンテナを起動:
   ```bash
   docker-compose up
   ```

   以下のメッセージが表示されます: `hello from docker`

### または、Docker CLIを使用する場合

1. Dockerイメージをビルド:
   ```bash
   docker build -t hello-docker ./hello-docker
   ```

2. コンテナを実行:
   ```bash
   docker run --rm hello-docker
   ```

   以下のメッセージが表示されます: `hello from docker`
