# Hello World Docker Application

This is a simple Docker application that prints "hello world".

## How to build and run
0. (ローカルで実行する場合)Docker Desktopを起動。仮想環境は`env2`

1. Build the Docker image:
   ```
   docker build -t hello-world hello-world/.
   ```

2. Run the Docker container:
   ```
   docker run hello-world
   ```

## Files

- `app.py`: Simple Python script that imports pandas and prints "hello world"
- `Dockerfile`: Docker configuration file
- `requirements.txt`: Python dependencies (pandas)