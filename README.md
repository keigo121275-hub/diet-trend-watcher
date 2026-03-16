# 🥗 ダイエットトレンドウォッチャー

毎朝8時に5サイトを自動巡回し、ダイエット関連キーワードにマッチした記事をAIで要約してWebページとして公開するツールです。

## 公開URL

`https://keigo121275-hub.github.io/diet-trend-watcher/`

## 機能

- **5サイト巡回**: PR TIMES / Fytte / Nikkei XTrend / 厚生労働省（2ページ）
- **キーワードフィルタ**: 170+のダイエット関連キーワードで自動絞り込み
- **AI要約**: GPT-4o mini で3〜4文に要約
- **自動公開**: GitHub Actions + GitHub Pages で毎朝自動更新

## セットアップ

### 1. GitHubシークレットにAPIキーを登録
Settings → Secrets and variables → Actions → New repository secret
- Name: `OPENAI_API_KEY`
- Secret: OpenAI APIキー

### 2. GitHub Pages を有効化
Settings → Pages → Source: `Deploy from a branch` → Branch: `main` / `docs`

### 3. 手動テスト実行
Actions → 毎朝8時 ダイエットトレンド収集 → Run workflow

## ローカル実行

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
python scraper.py
# docs/index.html が生成されます
```

## ファイル構成

```
diet-trend-watcher/
├── .github/workflows/daily_scrape.yml  # 自動実行スケジュール
├── docs/index.html                     # 公開ページ（自動生成）
├── scraper.py                          # メインスクリプト
├── requirements.txt
└── README.md
```
