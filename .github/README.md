# GCP Artifact Registry 自動デプロイ設定

このリポジトリには、hello-worldのDockerイメージをGoogle Cloud Platform (GCP) Artifact Registryに自動デプロイするGitHub Actionsワークフローが含まれています。

# memo

- **Artifact Registryリポジトリの作成**はterraformでやった方がよいかも（今回はUI上でやった）


## 前提条件

ワークフローを正常に実行するために、以下の設定が必要です：

### 1. GCP設定

1. **GCPプロジェクトの作成**（まだない場合）
   - 現在の設定では `trading-prod-468212` プロジェクトを使用

2. **必要なAPIの有効化**:
   ```bash
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

3. **Artifact Registryリポジトリの作成**:
   ```bash
   gcloud artifacts repositories create temp-repo \
     --repository-format=docker \
     --location=asia-northeast1 \
     --description="Temporary Docker repository for hello-world"
   ```

4. **サービスアカウントの作成**:
   ```bash
   gcloud iam service-accounts create github-actions \
     --description="Service account for GitHub Actions" \
     --display-name="GitHub Actions"
   ```

5. **必要な権限の付与**:
   ```bash
   gcloud projects add-iam-policy-binding trading-prod-468212 \
     --member="serviceAccount:github-actions@trading-prod-468212.iam.gserviceaccount.com" \
     --role="roles/artifactregistry.writer"
   
   gcloud projects add-iam-policy-binding trading-prod-468212 \
     --member="serviceAccount:github-actions@trading-prod-468212.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

6. **サービスアカウントキーの作成とダウンロード**:
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions@trading-prod-468212.iam.gserviceaccount.com
   ```

### 2. GitHubシークレットの設定

GitHubリポジトリに以下のシークレットを追加してください：

1. **GCP_SA_KEY**: `key.json`ファイルの全内容（サービスアカウントキー）

シークレットの追加方法：
1. GitHubリポジトリにアクセス
2. Settings → Secrets and variables → Actions に移動
3. "New repository secret" をクリック
4. 適切な名前と値でシークレットを追加

## ワークフローの詳細

ワークフロー（`build-and-push.yml`）の動作：

1. **トリガー**: mainブランチへのプッシュ時に、`hellow-world/`ディレクトリまたはワークフローファイル自体に変更があった場合
2. **ビルド**: `hellow-world/`ディレクトリからDockerイメージをビルド
3. **認証**: サービスアカウントキーを使用してGCPに認証
4. **プッシュ**: イメージをArtifact Registryに`latest`タグでプッシュ

## リポジトリ構造

デプロイ後、イメージは以下の場所で利用可能です：
```
asia-northeast1-docker.pkg.dev/trading-prod-468212/temp-repo/hellow-world:latest
```

## デプロイされたイメージの実行

デプロイされたイメージを実行するには：

```bash
# 最新のイメージをプルして実行
docker run asia-northeast1-docker.pkg.dev/trading-prod-468212/temp-repo/hellow-world:latest
```

## 設定のカスタマイズ

`.github/workflows/build-and-push.yml` で以下を変更できます：

- **プロジェクトID**: 現在は `trading-prod-468212` を使用
- **リポジトリ名**: 現在は `temp-repo` を使用
- **イメージ名**: 現在は `hello-world` を使用
- **リージョン**: 現在は `asia-northeast1`（東京）を使用
- **トリガーパス**: デプロイをトリガーするファイル変更のパス

## 注意事項

- ワークフローファイル内でプロジェクトIDが直接指定されています
- `hello-world` ディレクトリ名がパスで使用されています（hello-worldではなく）
- 本番環境では、プロジェクトやサービスアカウントを別途管理することを検討してください