#!/usr/bin/env python3
"""
Diet Trend Watcher
毎朝8時に5サイトを巡回し、キーワードにマッチした記事をGPTで要約してHTML化するツール
"""

import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# ============================================================
# 設定
# ============================================================

JST = timezone(timedelta(hours=9))

KEYWORDS = [
    "オートミール レシピ", "ダイエット 食事", "りんご酢ダイエット", "痩せる食事",
    "業務スーパー ダイエット", "オートミール", "脂質制限ダイエット", "コストコ ダイエット",
    "痩せるコーヒー", "オートミール 朝ごはん", "基礎代謝を上げる方法", "りんご酢 飲み方",
    "ダイエット レシピ", "ルイボスティー 効果", "もち麦", "りんご酢", "きなこ",
    "ダイエットコーヒー", "ココアパウダー ダイエット", "代謝を上げる方法", "鯖缶",
    "ココア ダイエット", "もち麦ダイエット", "食べて痩せる", "オーバーナイトオーツ",
    "ダイエット おやつ", "もち麦 効果", "りんご酢 効果", "りんご酢 おすすめ",
    "きな粉 ダイエット", "干し芋 ダイエット", "アーモンド", "ダイエット ヨーグルト",
    "ダイエット 食事 レシピ", "皮下脂肪の落とし方", "ヨーグルト おすすめ", "バナナダイエット",
    "食べ過ぎた次の日", "きな粉", "きな粉ダイエット", "スリモアコーヒー 効果",
    "脂肪燃焼スープ", "ソイプロテイン おすすめ", "プロテイン おすすめ 女性", "ココア",
    "生姜紅茶 ダイエット", "更年期 ダイエット", "サイゼリヤ ダイエット", "鯖缶 ダイエット",
    "脂肪肝 改善 食事", "プルーン 効果", "ダイエットスープ", "リンゴ酢",
    "オリーブオイル 効果", "きな粉効果", "きな粉 効果", "オートミール 食べ方",
    "大根おろし", "梅流し 作り方", "オートミールの食べ方", "ヨーグルト ダイエット",
    "スリモアコーヒー", "梅流し", "梅流しダイエット", "雑穀米",
    "ソイプロテイン おすすめ 女性", "きな粉コーヒー", "ヨーグルトダイエット", "甘酒",
    "16時間ダイエット", "缶詰ダイエット", "コーヒー ダイエット", "一ヶ月で5キロ痩せる方法",
    "オートミール ダイエット", "きな粉の食べ方", "コーヒーダイエット", "タンパクオトメ",
    "シナモン 効果", "純ココア", "痩せる飲み物", "ダイエット パン", "ダイエットおやつ",
    "1ヶ月で5キロ痩せる方法", "玄米 ダイエット", "食べ過ぎた時の対処法", "ダイエットレシピ",
    "きな粉ドリンク", "ルイボスティー", "はちみつレモン", "松田リエ レシピ",
    "鍋 ダイエット", "梅白湯", "ダイエット食事", "リンゴ酢の飲み方",
    "コストコ ダイエット食品", "もやしダイエット", "スタバ ダイエット", "梅流し 効果",
    "ококоパウダー", "シナモンコーヒー", "全粒粉 パン", "甘酒 効能",
    "タンパク質 ダイエット", "脂質制限", "痩せる 食事", "雑穀米ダイエット",
    "めかぶ", "脂肪肝 食事", "もち麦 炊き方", "りんご酢 レシピ",
    "サラダチキン ダイエット", "お米ダイエット", "オートミールレシピ", "ダイエット 停滞期",
    "サバ缶", "りんごダイエット", "鯖缶ダイエット", "純ococо ダイエット",
    "干し芋", "もやし ダイエット", "痩せない理由", "ダイエット 鍋",
    "おすすめプロテイン", "ダイエット お菓子", "妊娠中 ダイエット", "キャベツダイエット",
    "白湯 ダイエット", "グラノーラ ダイエット", "はちみつダイエット", "味噌汁ダイエット",
    "豆乳", "オートミール レシピ 朝食", "ヒルナンデス", "サイゼ ダイエット",
    "雑穀米 効果", "体脂肪を減らす方法", "食欲を抑える方法", "オートミール レシピ 簡単",
    "もち麦 おすすめ", "ococоダイエット", "鮭 ダイエット", "デトックススープ",
    "酢キャベツ 作り方", "オートミールご飯", "脂質制限 レシピ", "豆乳 ダイエット",
    "痩せる方法", "皮下脂肪の落とし方 女性", "オートミール 美味しい食べ方",
    "妊婦 体重管理", "きな粉 レシピ ダイエット", "豆腐ダイエット", "スムージー ダイエット",
    "置き換えダイエット プロテイン", "コーヒー シナモン", "業務スーパー",
    "トマトジュース ダイエット", "代謝を上げる", "バナナ ダイエット", "ダイエット 飲み物",
    "トマトジュース リンゴ酢", "ダイエット コーヒー", "ゆで卵 ダイエット",
    "食べて痩せるダイエット", "コストコダイエット", "ダイエット飯", "きな粉ヨーグルト",
    "豆乳ダイエット", "酢納豆", "アーモンドミルク きなこ", "アーモンド効果",
    "痩せる朝ごはん", "夜バナナ", "味噌汁 ダイエット", "アセロラ", "ソイプロテイン",
    "シボラナイトダイエットコーヒー", "豆乳 きな粉", "酢キャベツダイエット",
    "レモン水 効果", "オートミールダイエット", "きな粉 健康",
    # 重要な単体キーワード（マッチ率を高めるため追加）
    "ダイエット", "痩せる", "脂肪", "代謝", "食事制限", "カロリー",
    "糖質制限", "断食", "プロテイン", "サプリ", "栄養", "食物繊維",
    "腸活", "デトックス", "体重", "BMI", "肥満", "やせ", "減量",
]

SITES = [
    {
        "name": "PR TIMES",
        "url": "https://prtimes.jp/",
        "type": "prtimes",
        "color": "#003087",
        "bg": "#e8f0fe",
    },
    {
        "name": "Fytte",
        "url": "https://fytte.jp/",
        "type": "fytte",
        "color": "#d81b60",
        "bg": "#fce4ec",
    },
    {
        "name": "Nikkei XTrend",
        "url": "https://xtrend.nikkei.com/",
        "type": "xtrend",
        "color": "#c62828",
        "bg": "#ffebee",
    },
    {
        "name": "厚生労働省",
        "url": "https://www.mhlw.go.jp/stf/news.rdf",
        "type": "mhlw_rss",
        "color": "#1565c0",
        "bg": "#e3f2fd",
    },
    {
        "name": "厚労省（特定健診）",
        "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000161103.html",
        "type": "mhlw_page",
        "color": "#2e7d32",
        "bg": "#e8f5e9",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

MAX_ARTICLES_PER_SITE = 40
MAX_MATCHED_PER_SITE = 5
DOCS_DIR = Path(__file__).parent / "docs"


# ============================================================
# ユーティリティ
# ============================================================

def fetch(url: str, timeout: int = 20) -> str | None:
    """URLのHTMLを取得する"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except Exception as e:
        print(f"  [ERROR] fetch failed: {url} — {e}")
        return None


def matches_keywords(text: str) -> list[str]:
    """テキストにマッチするキーワードのリストを返す（重複なし、優先度順）"""
    matched = []
    seen = set()
    for kw in KEYWORDS:
        kw_norm = kw.lower().replace(" ", "")
        text_norm = text.lower().replace(" ", "").replace("　", "")
        if kw_norm not in seen and kw_norm in text_norm:
            matched.append(kw)
            seen.add(kw_norm)
    return matched


def extract_article_text(url: str) -> str:
    """記事URLからメインテキストを抽出する"""
    if not url or url.endswith(".pdf"):
        return ""
    html = fetch(url)
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
        tag.decompose()
    for selector in [
        "article",
        "[class*='article-body']",
        "[class*='article-content']",
        "[class*='entry-content']",
        "[class*='post-content']",
        "[class*='article__body']",
        "main",
        "[class*='content']",
    ]:
        el = soup.select_one(selector)
        if el:
            text = el.get_text(separator="\n", strip=True)
            if len(text) > 150:
                return text[:3000]
    body = soup.find("body")
    if body:
        return body.get_text(separator="\n", strip=True)[:3000]
    return ""


# ============================================================
# サイト別スクレイパー
# ============================================================

def scrape_prtimes() -> list[dict]:
    """PR TIMESからプレスリリースを取得"""
    print("  Scraping PR TIMES...")
    articles = []
    html = fetch("https://prtimes.jp/")
    if not html:
        return articles

    soup = BeautifulSoup(html, "html.parser")
    seen_urls = set()

    # タイトルリンクを幅広く収集
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # PRTIMESの記事URL形式にマッチするものだけ
        if not re.search(r"/main/html/(rd|index)", href):
            continue
        if not href.startswith("http"):
            href = "https://prtimes.jp" + href
        if href in seen_urls:
            continue
        seen_urls.add(href)

        # タイトルテキストを取得
        title = a.get_text(strip=True)
        if not title or len(title) < 5 or len(title) > 200:
            continue

        # 日付を近くから探す
        parent = a.find_parent()
        date_el = parent.find("time") if parent else None
        date_text = date_el.get_text(strip=True) if date_el else ""

        articles.append({"title": title, "url": href, "date": date_text})
        if len(articles) >= MAX_ARTICLES_PER_SITE:
            break

    # フォールバック: h3要素を探す
    if not articles:
        for h3 in soup.select("h3")[:MAX_ARTICLES_PER_SITE]:
            title = h3.get_text(strip=True)
            a = h3.find("a") or h3.find_parent("a")
            if not a:
                p = h3.find_parent()
                a = p.find("a") if p else None
            url = ""
            if a and a.get("href"):
                url = a["href"]
                if not url.startswith("http"):
                    url = "https://prtimes.jp" + url
            if title:
                articles.append({"title": title, "url": url, "date": ""})

    return articles


def scrape_fytte() -> list[dict]:
    """Fytteから記事を取得"""
    print("  Scraping Fytte...")
    articles = []
    html = fetch("https://fytte.jp/")
    if not html:
        return articles

    soup = BeautifulSoup(html, "html.parser")
    seen_urls = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "fytte.jp/news/" not in href and not href.startswith("/news/"):
            continue
        if not href.startswith("http"):
            href = "https://fytte.jp" + href
        if href in seen_urls:
            continue
        seen_urls.add(href)

        title = a.get_text(strip=True)
        if not title or len(title) < 5:
            # 近くのh2/h3を探す
            parent = a.find_parent()
            heading = parent.find(["h2", "h3", "h4"]) if parent else None
            title = heading.get_text(strip=True) if heading else ""

        if not title or len(title) < 5:
            continue

        # 日付を探す
        parent = a.find_parent()
        date_el = (
            parent.find("time") or
            parent.find(class_=re.compile(r"date|time"))
        ) if parent else None
        date_text = date_el.get_text(strip=True) if date_el else ""

        articles.append({"title": title, "url": href, "date": date_text})
        if len(articles) >= MAX_ARTICLES_PER_SITE:
            break

    return articles


def scrape_xtrend() -> list[dict]:
    """Nikkei X Trendから記事タイトルを取得（無料部分のみ）"""
    print("  Scraping Nikkei XTrend...")
    articles = []
    html = fetch("https://xtrend.nikkei.com/")
    if not html:
        return articles

    soup = BeautifulSoup(html, "html.parser")
    seen_urls = set()

    # 日付見出しと記事リストを取得
    current_date = ""
    for el in soup.find_all(["h2", "li", "a"]):
        if el.name == "h2":
            text = el.get_text(strip=True)
            date_match = re.search(r"\d+月\d+日", text)
            if date_match:
                current_date = date_match.group(0)
        elif el.name == "a":
            href = el.get("href", "")
            if "/atcl/contents/" not in href:
                continue
            if not href.startswith("http"):
                href = "https://xtrend.nikkei.com" + href
            href = href.split("?")[0]
            if href in seen_urls:
                continue
            seen_urls.add(href)
            title = el.get_text(strip=True)
            if title and len(title) > 5:
                articles.append({"title": title, "url": href, "date": current_date})
            if len(articles) >= MAX_ARTICLES_PER_SITE:
                break

    return articles


def scrape_mhlw_rss() -> list[dict]:
    """厚生労働省のRSSフィードから記事を取得"""
    print("  Scraping MHLW RSS...")
    articles = []

    try:
        resp = requests.get(
            "https://www.mhlw.go.jp/stf/news.rdf",
            headers=HEADERS,
            timeout=20
        )
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        # RDF形式のネームスペースに対応
        namespaces = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rss": "http://purl.org/rss/1.0/",
            "dc": "http://purl.org/dc/elements/1.1/",
        }
        items = (
            root.findall("{http://purl.org/rss/1.0/}item") or
            root.findall(".//item")
        )
        for item in items[:MAX_ARTICLES_PER_SITE]:
            title_el = item.find("{http://purl.org/rss/1.0/}title") or item.find("title")
            link_el = item.find("{http://purl.org/rss/1.0/}link") or item.find("link")
            date_el = (
                item.find("{http://purl.org/dc/elements/1.1/}date") or
                item.find("pubDate")
            )
            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            url = link_el.text.strip() if link_el is not None and link_el.text else ""
            date = date_el.text.strip() if date_el is not None and date_el.text else ""
            if title and url:
                articles.append({"title": title, "url": url, "date": date})
    except ET.ParseError:
        # RDFパース失敗時はHTMLとして取得
        print("  [WARN] RSS parse failed, falling back to HTML scraping...")
        html = fetch("https://www.mhlw.go.jp/stf/new-info/")
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.select("a[href]")[:MAX_ARTICLES_PER_SITE]:
                href = a["href"]
                if not href.startswith("http"):
                    href = "https://www.mhlw.go.jp" + href
                title = a.get_text(strip=True)
                if title and "mhlw.go.jp" in href:
                    articles.append({"title": title, "url": href, "date": ""})
    except Exception as e:
        print(f"  [ERROR] MHLW RSS: {e}")

    return articles


def scrape_mhlw_page() -> list[dict]:
    """厚労省 特定健診ページから更新情報を取得"""
    print("  Scraping MHLW 特定健診ページ...")
    articles = []
    url = "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000161103.html"
    html = fetch(url)
    if not html:
        return articles

    soup = BeautifulSoup(html, "html.parser")
    seen_urls = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get_text(strip=True)
        if not title or len(title) < 8:
            continue
        if not href.startswith("http"):
            href = "https://www.mhlw.go.jp" + href
        if href in seen_urls or "mhlw.go.jp" not in href:
            continue
        seen_urls.add(href)

        date_match = re.search(r"\d{4}年\d{1,2}月\d{1,2}日", title)
        date_text = date_match.group(0) if date_match else ""
        articles.append({"title": title, "url": href, "date": date_text})
        if len(articles) >= MAX_ARTICLES_PER_SITE:
            break

    return articles


SCRAPERS = {
    "prtimes": scrape_prtimes,
    "fytte": scrape_fytte,
    "xtrend": scrape_xtrend,
    "mhlw_rss": scrape_mhlw_rss,
    "mhlw_page": scrape_mhlw_page,
}


# ============================================================
# GPT要約
# ============================================================

def summarize_article(client: OpenAI, title: str, content: str, matched_kw: list[str]) -> str:
    """GPTで記事を要約する"""
    if not content or len(content) < 100:
        content = "（記事本文を取得できませんでした）"

    kw_text = "、".join(matched_kw[:5])
    prompt = (
        f"以下のダイエット・健康記事を3〜4文で日本語で要約してください。"
        f"関連キーワード「{kw_text}」に関連する重要なポイント、"
        f"具体的な方法や効果があれば強調してください。\n\n"
        f"タイトル: {title}\n\n"
        f"記事内容:\n{content[:2500]}\n\n"
        f"要約（3〜4文）:"
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"  [ERROR] GPT summarization failed: {e}")
        return f"（要約を生成できませんでした: {e}）"


# ============================================================
# HTML生成
# ============================================================

def generate_html(results: list[dict], generated_at: datetime) -> str:
    """収集・要約した記事をBeautiful HTMLに変換する"""
    date_str = generated_at.strftime("%Y年%m月%d日 %H:%M")

    if not results:
        articles_html = """
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <p>本日はキーワードにマッチする記事が見つかりませんでした。</p>
        </div>
        """
    else:
        cards = []
        for r in results:
            kw_tags = "".join(
                f'<span class="kw-tag">{kw}</span>'
                for kw in r["matched_keywords"][:6]
            )
            date_html = f'<span class="article-date">{r["date"]}</span>' if r.get("date") else ""
            card = f"""
            <div class="card">
                <div class="card-header">
                    <span class="source-badge" style="background:{r['color']}">{r['site_name']}</span>
                    {date_html}
                </div>
                <h2 class="card-title">
                    <a href="{r['url']}" target="_blank" rel="noopener">{r['title']}</a>
                </h2>
                <div class="keywords">{kw_tags}</div>
                <div class="summary">{r['summary']}</div>
                <a class="read-more" href="{r['url']}" target="_blank" rel="noopener">
                    記事を読む →
                </a>
            </div>
            """
            cards.append(card)
        articles_html = "\n".join(cards)

    total = len(results)
    site_counts = {}
    for r in results:
        site_counts[r["site_name"]] = site_counts.get(r["site_name"], 0) + 1

    stats_items = "".join(
        f'<span class="stat-item"><strong>{name}</strong> {count}件</span>'
        for name, count in site_counts.items()
    )

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ダイエットトレンドウォッチャー</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Sans', 'Hiragino Kaku Gothic ProN',
                   'Noto Sans JP', sans-serif;
      background: #f5f7fa;
      color: #1a1a2e;
      line-height: 1.7;
      min-height: 100vh;
    }}

    /* ---- ヘッダー ---- */
    .header {{
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 40px 24px 32px;
      text-align: center;
    }}
    .header-icon {{ font-size: 48px; margin-bottom: 12px; }}
    .header h1 {{
      font-size: clamp(1.5rem, 4vw, 2.2rem);
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 8px;
    }}
    .header-sub {{ opacity: 0.9; font-size: 0.95rem; }}
    .update-time {{
      display: inline-block;
      margin-top: 16px;
      background: rgba(255,255,255,0.2);
      border-radius: 20px;
      padding: 6px 18px;
      font-size: 0.85rem;
    }}

    /* ---- 統計バー ---- */
    .stats-bar {{
      background: white;
      border-bottom: 1px solid #e8ecf0;
      padding: 14px 24px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      font-size: 0.85rem;
      color: #555;
    }}
    .stats-bar .total {{
      font-weight: 700;
      color: #667eea;
      font-size: 1rem;
    }}
    .stat-item {{
      background: #f0f2f8;
      border-radius: 12px;
      padding: 4px 12px;
    }}

    /* ---- メインコンテンツ ---- */
    .main {{
      max-width: 960px;
      margin: 0 auto;
      padding: 32px 16px 64px;
    }}

    /* ---- カード ---- */
    .card {{
      background: white;
      border-radius: 16px;
      padding: 24px 28px;
      margin-bottom: 20px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06);
      border: 1px solid #edf0f7;
      transition: box-shadow 0.2s, transform 0.2s;
    }}
    .card:hover {{
      box-shadow: 0 8px 30px rgba(0,0,0,0.12);
      transform: translateY(-2px);
    }}
    .card-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .source-badge {{
      color: white;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 4px 12px;
      border-radius: 20px;
      letter-spacing: 0.3px;
      flex-shrink: 0;
    }}
    .article-date {{
      font-size: 0.8rem;
      color: #888;
    }}
    .card-title {{
      font-size: 1.1rem;
      font-weight: 700;
      line-height: 1.5;
      margin-bottom: 12px;
    }}
    .card-title a {{
      color: #1a1a2e;
      text-decoration: none;
    }}
    .card-title a:hover {{
      color: #667eea;
    }}
    .keywords {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 14px;
    }}
    .kw-tag {{
      background: #f0f2ff;
      color: #667eea;
      font-size: 0.75rem;
      padding: 3px 10px;
      border-radius: 12px;
      font-weight: 600;
    }}
    .summary {{
      font-size: 0.92rem;
      color: #444;
      line-height: 1.8;
      margin-bottom: 16px;
      padding: 14px 16px;
      background: #f8f9fc;
      border-left: 3px solid #667eea;
      border-radius: 0 8px 8px 0;
    }}
    .read-more {{
      font-size: 0.85rem;
      color: #667eea;
      font-weight: 600;
      text-decoration: none;
    }}
    .read-more:hover {{ text-decoration: underline; }}

    /* ---- 空の状態 ---- */
    .empty-state {{
      text-align: center;
      padding: 80px 24px;
      color: #888;
    }}
    .empty-icon {{ font-size: 64px; margin-bottom: 16px; }}

    /* ---- フッター ---- */
    .footer {{
      text-align: center;
      padding: 24px;
      font-size: 0.8rem;
      color: #aaa;
      border-top: 1px solid #e8ecf0;
    }}

    @media (max-width: 600px) {{
      .card {{ padding: 18px; }}
      .header {{ padding: 28px 16px 24px; }}
    }}
  </style>
</head>
<body>

<header class="header">
  <div class="header-icon">🥗</div>
  <h1>ダイエットトレンドウォッチャー</h1>
  <p class="header-sub">5サイトを毎朝8時に巡回 ✕ AIで自動要約</p>
  <div class="update-time">最終更新: {date_str} JST</div>
</header>

<div class="stats-bar">
  <span class="total">本日 {total}件の記事をキャッチ</span>
  {stats_items}
</div>

<main class="main">
  {articles_html}
</main>

<footer class="footer">
  <p>キーワード数: {len(KEYWORDS)}語 ／ 対象サイト: PR TIMES・Fytte・Nikkei XTrend・厚生労働省（2サイト）</p>
  <p style="margin-top:4px">Powered by Python + OpenAI GPT-4o mini + GitHub Actions + GitHub Pages</p>
</footer>

</body>
</html>
"""


# ============================================================
# メイン処理
# ============================================================

def main():
    print("=" * 60)
    print("Diet Trend Watcher 起動")
    print("=" * 60)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY が設定されていません")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    now = datetime.now(JST)
    all_results = []

    for site in SITES:
        print(f"\n[{site['name']}] 巡回中...")
        scraper = SCRAPERS.get(site["type"])
        if not scraper:
            continue

        raw_articles = scraper()
        print(f"  取得件数: {len(raw_articles)}")

        matched_count = 0
        for article in raw_articles:
            if matched_count >= MAX_MATCHED_PER_SITE:
                break

            matched_kw = matches_keywords(article["title"])
            if not matched_kw:
                continue

            print(f"  ✓ マッチ: {article['title'][:50]}...")
            print(f"    キーワード: {', '.join(matched_kw[:3])}")

            # 記事本文を取得
            content = extract_article_text(article["url"]) if article.get("url") else ""
            time.sleep(1)

            # GPTで要約
            summary = summarize_article(client, article["title"], content, matched_kw)

            all_results.append({
                "site_name": site["name"],
                "color": site["color"],
                "bg": site["bg"],
                "title": article["title"],
                "url": article["url"],
                "date": article.get("date", ""),
                "matched_keywords": matched_kw,
                "summary": summary,
            })
            matched_count += 1
            time.sleep(0.5)

        print(f"  マッチ件数: {matched_count}")

    print(f"\n合計 {len(all_results)} 件の記事を収集しました")

    # HTML生成
    DOCS_DIR.mkdir(exist_ok=True)
    html = generate_html(all_results, now)
    output_path = DOCS_DIR / "index.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"\nHTML生成完了: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
