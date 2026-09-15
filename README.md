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

## Architecture

```text
idol-db ───────┐
               │
owarai-live ───┤
               │
other sources ─┤
               ↓
          STAGE-Search
               ↓
        Event normalization
               ↓
          events.jsonl
               ↓
          week filter
               ↓
          今週のSTAGE
```

## Event model

共通の基本属性は `when / where / what / who / category / organizer / price / url / source`。

STAGE-Search は特定ジャンルのDBではなく、複数のイベントソースを横断して「いつ・どこで・何があるか」を探すための上位レイヤーとする。
