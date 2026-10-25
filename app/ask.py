"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 初期質問のあと、続けて質問できる

ツールは使わないが、同じ実行中の会話履歴を保持する「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors, types

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str, chat=None, temperature: float | None = None) -> str:
    if chat is None:
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL)

    config = None
    if temperature is not None:
        config = types.GenerateContentConfig(temperature=temperature)

    if config is None:
        response = chat.send_message(question)
    else:
        response = chat.send_message(question, config=config)

    # TODO(第1回 演習): response.usage_metadata から
    #   入力トークン数と出力トークン数を表示してみよう（Copilotに頼んでよい）

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="モデルの温度設定 (例: 0.0 ~ 1.0)。大きいほど創造的になる",
    )
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    if args.temperature is not None:
        print(f"[temperature] {args.temperature}")
    try:
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL)
        question = args.question
        while question:
            print(f"[質問] {question}\n")
            print(ask(question, chat=chat, temperature=args.temperature))
            question = input("\n[続けて質問] ")
            if question.strip().lower() in {"q", "quit", "exit"}:
                break
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)
    except EOFError:
        pass


if __name__ == "__main__":
    main()
