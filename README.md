# STAGE-Search

人が集まり、何かが起きる「STAGE」を横断検索するイベント探索基盤。

ライブだけに限定せず、参加できる予定・催しを共通の Event モデルで扱う。

## Categories

- `music` — 音楽・ライブ・コンサート
- `idol` — アイドル
- `owarai` — お笑い
- `theater` — 演劇・ミュージカル
- `festival` — お祭り・フェス・地域イベント
- `traditional` — 伝統芸能・落語・講談
- `talk` — 講演会・トークイベント
- `exhibition` — 展覧会・展示
- `workshop` — ワークショップ・体験
- `sports` — スポーツ・観戦
- `other` — その他

## Crawl / Publish Policy

**イベントは価格に関係なく検索・収集する。公開掲載は500円以下を基本とする。**

```text
crawl / discover: all events
        ↓
canonical / latest DB: all observed events
        ↓
public discovery: ticket option <= 500円
```

500円を超えるイベントや価格不明イベントも収集DBから削除しない。検索・検証・履歴のために保持する。

500円は法律上の転載許可ラインではなく、STAGE-Searchのサービス上の公開基準である。公開データの利用では、出典URL・取得時刻・provenanceを保持し、元サイトの文章や画像を大量転載しない。

## AW — Agentic Discovery

AWは単純な全文検索ではなく、自然言語IntentをEvent / Venue / Provider / Organizer / Performer / Ticket / Sourceへ分解し、関係を辿って候補を発見・正規化・検証する。

```text
Intent
  ↓
Semantic Facet
  ↓
Search Graph
  ↓
Provider / Venue / Organizer / Performer
  ↓
Candidate Event
  ↓
Normalize → Dedupe → Verify
  ↓
Asset + Relation
  ↓
Public Discovery (<=500円)
```

### Idol Live

`idol-db`をアイドル領域のcanonical sourceとして接続する。アイドルライブについては、TIGET、LivePocket、プレイガイド、運営・事務所、主催者、会場などを横断して候補を収集する。

検索例:

- 「新宿で今日の無銭アイドルライブ」
- 「500円以下のアイドルライブ」
- 「TIGETのアイドルライブ」
- 「女性アイドルで今週」
- 「この会場で過去にやったアイドルライブ」
- 「特典会ありの無料ライブ」

## Event Search Agent

`python scripts/event_agent.py` が `sources.yaml` の公開データを取得し、共通 Event モデルへ正規化する。

出力:

- `data/events.jsonl` — 全イベントの正規化インデックス
- `data/week.json` — 今日から7日間のイベント

現在の一次ソース:

- `idol-db` — IDOL Watch / アイドルライブDB
- `owarai-live` — お笑いライブDB

ソースは `sources.yaml` に追加できる。将来的に演劇・祭り・講演会・展示・伝統芸能などを同じモデルへ接続する。

## Architecture

```text
idol-db ───────┐
owarai-live ───┤
other sources ─┘
               ↓
        STAGE Event Search Agent
               ↓
      Event + Venue normalization
               ↓
       all-events canonical index
               ↓
          AW semantic search
               ↓
       public <= 500円 filter
               ↓
          今週のSTAGE
```

## Event model

共通の基本属性は `when / where / what / who / category / organizer / price / url / source`。

価格情報は可能なら券種単位で保持する。`price`, `condition`, `drink_required`, `source_url`を分離し、「無銭0円 + 1D」のようなイベントを正しく検索できるようにする。

STAGE-Search は特定ジャンルのDBではなく、複数のイベントソースを横断して「いつ・どこで・何があるか」を探すための上位レイヤーとする。
