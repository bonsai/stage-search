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

## Event Search Agent

`python scripts/event_agent.py` が `sources.yaml` の公開データを取得し、共通 Event モデルへ正規化する。

出力:

- `data/events.jsonl` — 全イベントの正規化インデックス
- `data/week.json` — 今日から7日間のイベント

現在の一次ソース:

- `idol-db` — IDOL Watch
- `owarai-live` — お笑いライブDB

ソースは `sources.yaml` に追加できる。将来的に演劇・祭り・講演会・展示・伝統芸能などを同じモデルへ接続する。

## Architecture

```text
idol-db ───────┐
owarai-live ───┤
               ├──→ STAGE Event Search Agent
other sources ─┘              │
                              ↓
                       Event normalization
                              ↓
                         events.jsonl
                              ↓
                          week.json
                              ↓
                       今週のSTAGE
```

## Event model

共通の基本属性は `when / where / what / who / category / organizer / price / url / source`。

STAGE-Search は特定ジャンルのDBではなく、複数のイベントソースを横断して「いつ・どこで・何があるか」を探すための上位レイヤーとする。
