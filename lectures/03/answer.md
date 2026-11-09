# 第3回 解答 (Lecture 3 Answers)

## 演習 (Exercises)

- 第1回（素のLLM）とエージェントの回答の違い：
  - **第1回（素のLLM: `app.ask`）**:
    モデル（Gemini）自身の事前学習重みのみに依存しているため、「AIE2026の講座で使う『lecNN-start タグ』とは何ですか？」「宿題の3レベルとは？」といった講座特有の独自概念に対しては、「存じ上げません」「一般的な Git のタグ運用を説明します」と答えるか、あるいはもっともらしい一般的な推測（ハルシネーション）を返していた。
  - **第3回（エージェント: `app.agent`）**:
    モデルが自律的にプロンプト指示（`INSTRUCTIONS`）を解釈し、講座固有の語彙であると判断して `search_glossary` ツールを呼び出した。ローカルの `data/glossary.json` から正確な定義を取得した上で、「講義開始時点のひな形コードを指すタグであること」「未完了の回があってもその回の開始状態から始められること」を回答し、指示通り末尾に「関係する回: 第1回 / 第3回」を明記した正確かつ根拠のある回答を生成した。

- `--trace` で見えたツール呼び出し（ツール名と引数）：
  - コマンド: `uv run python -m app.agent --trace "LoRAとQLoRAの違いは？"`
  ```text
  --- trace ---
  [tool call]   search_glossary({'query': 'LoRA'})
  [tool call]   search_glossary({'query': 'QLoRA'})
  [tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "元の重みを固定し、小さな低ランク行列（アダプタ）だけを追加して学習するPEFTの一種。VRAMと学習時間を大幅に節約できる。", "related": ["peft", "qlora", "lora-r", "lora-alpha"]}]…
  [tool return] search_glossary -> [{"term": "QLoRA", "lecture": 2, "definition": "基盤モデルを4bitに量子化してVRAM消費を抑え、その上でLoRAアダプタを学習する手法。通常のLoRAよりさらに小さなGPUで動かせるが、計算はfloat16などで行う。", "related": ["lora", "quantization", "peft"]}]…
  [usage] RunUsage(requests=2, request_tokens=1840, response_tokens=312, total_tokens=2152)
  ```

- 1つの質問での LLM 呼び出し回数（`requests`）：
  - **`requests = 2`**
    - **1回目の呼び出し**: ユーザーの質問「LoRAとQLoRAの違いは？」を入力として受け取り、モデルが2つのツール呼び出し（`search_glossary({'query': 'LoRA'})` と `search_glossary({'query': 'QLoRA'})`）を決定して出力。
    - **2回目の呼び出し**: プログラムがツールを実行して得た2件の検索結果（`ToolReturnPart`）をコンテキストに含めてモデルに再入力し、モデルが比較解説文を最終回答として生成。

- 追加したツールと、docstring に書いた説明：
  - **関数名**: `make_quiz(lecture: int) -> str`
  - **docstring**:
    ```python
    def make_quiz(lecture: int) -> str:
        """指定した講義回（1始まりの整数）の用語集から1つを選び、復習用の確認問題と答えを返す。

        「第2回から確認問題を出して」「復習クイズを作って」のように、
        学習者が復習問題やクイズを求めたときに使う。
        """
    ```
  - **実装の特徴**: `load_glossary()` から指定講義の用語を抽出し、`random.choice` で1件選んで `{"question": "...", "answer": "..."}` 形式のJSON文字列を返す。該当する回が存在しない場合（`lecture=0` や `lecture=99` など）でも例外でクラッシュせず、用意されている講義回を案内するフォールバック処理を実装した。

---

## 宿題 (Homework)

本解答では、**基礎 (Basic)**、**実装 (Implementation)**、**発展 (Advanced a / b)** の全レベルを網羅して完了しました。

---

### 基礎 (Basic Tier)

- **取り組んだ内容**:
  `app/agent.py` の `INSTRUCTIONS` および `app/tools.py` のツール docstring を段階的に書き換え、同一の質問に対する `--trace` の挙動（ツール呼び出し順序、呼び出し回数、引数、LLMの呼び出し回数、最終回答の品質）がどう変化するかを詳細に記録・比較した。

- **実験1: `INSTRUCTIONS` から用語集の検索ルールを削除**:
  - **変更内容**: `INSTRUCTIONS` 内の「用語や講座に固有のことを答える前に、必ず search_glossary で用語集を確認する。」を削除。
  - **質問**: `uv run python -m app.agent --trace "LoRAとQLoRAの違いは？"`
  - **結果（変更前）**:
    - `[tool call] search_glossary({'query': 'LoRA'})`
    - `[tool call] search_glossary({'query': 'QLoRA'})`
    - `[usage] requests=2, tool_calls=2`
  - **結果（変更後）**:
    - ツール呼び出しが一切行われず、即座に事前学習の一般知識で回答した。
    - `[usage] requests=1, tool_calls=0`
  - **考察**: 「必ず検索せよ」という強制ルールを取り除くと、モデルは自身の重み内知識で回答できると過信し、ツール実行をスキップする。これによりリクエスト回数とレイテンシは半減するが、講座固有の用語定義や関連講義番号の付与は行われなくなった。

- **実験2: `search_glossary` の docstring による引数制約の変更**:
  - **変更内容**: docstring の「query には調べたい用語を1つだけ入れる（例: 'LoRA'）」を、「query には調べたい用語を空白またはカンマ区切りで複数まとめて渡してもよい」に変更。
  - **質問**: `uv run python -m app.agent --trace "LoRAとQLoRAの違いは？"`
  - **結果（変更後）**:
    - `[tool call] search_glossary({'query': 'LoRA QLoRA'})` (1回のツール呼び出しに集約)
    - `[usage] requests=2, tool_calls=1`
  - **考察**: ツールの引数仕様（docstring）を書き換えるだけで、モデルの計画（Planner）能力が変化し、並列複数呼び出しから一括呼び出しへとプランニングが変化した。ツール設計における docstring がAPIシグネチャ以上の「行動仕様書」として機能していることが確認できた。

---

### 実装 (Implementation Tier)

- **取り組んだ内容**:
  学習者の学習記録を `learning_log/` フォルダにJSON形式で永続化する `save_learning_log` ツールを `app/tools.py` に作成し、`app/agent.py` に `requires_approval=True` を指定して登録。実行前に利用者の承諾を求める Human-in-the-Loop（人間の介入による承認フロー）を実装した。また、`tests/test_agent.py` および `tests/test_tools.py` に `TestModel` を用いた単体テストを追加した。

- **`app/tools.py` への実装**:
  ```python
  def save_learning_log(topic: str, notes: str, lecture: int | None = None) -> str:
      """学習の記録やメモを learning_log/ フォルダに保存する。

      「今日の学習内容を記録して」「メモを保存して」のように、学習記録の
      保存を指示されたときに使う。保存は取り消しにくいため、実行前に利用者の確認を挟む。
      """
      log_dir = Path(__file__).resolve().parent.parent / "learning_log"
      log_dir.mkdir(parents=True, exist_ok=True)
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
      clean_topic = _normalize(topic)[:30] or "untitled"
      log_file = log_dir / f"{timestamp}_{clean_topic}.json"
      entry = {
          "timestamp": datetime.now().isoformat(),
          "topic": topic,
          "lecture": lecture,
          "notes": notes,
      }
      log_file.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
      return f"学習記録を保存しました: {log_file.name}"
  ```

- **`app/agent.py` での承認配線**:
  ```python
  from pydantic_ai import Agent, DeferredToolRequests

  agent = Agent(instructions=INSTRUCTIONS, output_type=[str, DeferredToolRequests])
  agent.tool_plain(tools.search_glossary)
  agent.tool_plain(tools.get_lecture_summary)
  agent.tool_plain(tools.make_quiz)
  agent.tool_plain(tools.save_learning_log, requires_approval=True)
  ```
  CLI実行時（`main`）、`save_learning_log` が呼ばれると即座には実行されず、`DeferredToolRequests` が返却される。CLIはユーザーに「このツールを実行してよろしいですか？ [y/N]: 」と確認を求め、`y` の場合のみ実体を呼び出して保存を確定する。

- **テストの追加と検証**:
  - `tests/test_tools.py`: 正常に `learning_log/` 配下にファイルが作成され、JSON内容（topic, lecture, notes, timestamp）が一致することを検証。
  - `tests/test_agent.py`: `TestModel(call_tools=["save_learning_log"])` を用いて、APIキー不要の状態で `DeferredToolRequests` が正しくトリガーされることを検証。

---

### 発展 (Advanced Tier)

本課題では、**(a) Google ADK による再構築** と **(b) コーディングエージェント Pi のシステムプロンプト比較** の双方を実施した。

#### 発展 (a): Google ADK (Agent Development Kit) によるエージェント再構築

- **実装ファイル**:
  - `adk_agent/glossary_agent/__init__.py`: `from . import agent`
  - `adk_agent/glossary_agent/agent.py`:
  ```python
  from google.adk.agents import Agent
  from app import tools
  from app.agent import INSTRUCTIONS

  root_agent = Agent(
      model="gemini-3.5-flash-lite",
      name="glossary_agent",
      instruction=INSTRUCTIONS,
      tools=[tools.search_glossary, tools.get_lecture_summary, tools.make_quiz],
  )
  ```

- **Pydantic AI と Google ADK の比較考察**:
  1. **エージェント定義と責務の分離**:
     - *Pydantic AI*: モデル実行環境（`TestModel` や `GoogleModel`）を実行時（`run_sync`）に注入（Dependency Injection）する設計。テスト容易性が高く、CLIやWebなど任意のホストに埋め込みやすい。
     - *Google ADK*: `Agent` インスタンス自身がモデル名・指示・ツール一式を宣言的に保持する構成。`adk run` や `adk web` といったCLI/Webサーバーエコシステムと直結しており、素早いプロトタイピングに適している。
  2. **ツール登録のインターフェース**:
     - *Pydantic AI*: `agent.tool_plain()` や `agent.tool()` など、コンテキスト依存の有無や承認要否（`requires_approval`）を細かく制御できる。
     - *Google ADK*: `tools=[...]` に関数リストを渡すだけで、Pythonの型ヒントとdocstringからGeminiのFunction Calling用スキーマが自動生成される極めてシンプルなAPI。

#### 発展 (b): コーディングエージェント Pi のシステムプロンプト比較

公開リポジトリ（`earendil-works/pi` の `packages/coding-agent/src/core/system-prompt.ts`）で公開されている Pi のシステムプロンプトと、本講座の学習支援エージェントの `INSTRUCTIONS` を比較分析した。

- **比較表**:

| 項目 | 本講座の学習支援エージェント (`INSTRUCTIONS`) | コーディングエージェント Pi (`system-prompt.ts`) |
|---|---|---|
| **自律性と承認** | `requires_approval=True` による慎重な事前確認（ファイル書き込み等はユーザーに問いかける）。 | **完全自律型（Zero-shot Action）**。コマンド実行やファイル編集をいちいち確認せず自律的に実行して結果を報告する。 |
| **教育方針・回答スタイル** | **「ヒントで導く」**。宿題の解答そのものは出力せず、学習者に思考のプロセスを促す。 | **「直接実装・修正する」**。具体的なコードブロック、パッチ、コマンドを最小限の装飾で直接提供する。 |
| **事実の根拠（Grounding）** | 用語集（`glossary.json`）を絶対の正解とし、未記載の事実は「用語集にない」と明言することを義務付け。 | リポジトリ内のファイルを検索（read_file, run_command）し、既存コード規約に合わせることを重視。 |
| **コンテキスト管理** | 最小限の制約文（約10行のコンパクトなプロンプト）。 | エディタ設定、差分形式、Git運用、エラー回復手順など多岐にわたる実践的ルール群（数百行）。 |

- **気づきと学び**:
  エージェントのシステムプロンプトは単なる役割付け（Persona）ではなく、**「そのエージェントの自律性の度合い（確認を挟むか即座に実行するか）」** と **「目的（学習者を自立させる教育目的か、作業を代行する生産性目的か）」** を決定付ける最重要の制御パラメータであることが深く実感できた。
