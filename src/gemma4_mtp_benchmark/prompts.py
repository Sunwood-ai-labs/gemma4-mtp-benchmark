from __future__ import annotations

PROMPT_SETS = {
    "quick": [
        """日本語で、Multi-Token Prediction がLLMの生成を高速化する仕組みを
5文で説明してください。""",
    ],
    "coding": [
        """Pythonで小さなCLIツールを書いてください。
要件:
- URLを引数で受け取る
- requestsでHTMLを取得する
- BeautifulSoupでtitleタグを取り出す
- 例外処理を入れる
- 最後に使い方を日本語で説明する""",
        """次の仕様でPythonコードを書いてください。
CLI引数でURLを受け取り、requestsとBeautifulSoupを使ってtitleタグを取得します。
例外処理、型ヒント、使い方の説明も含めてください。""",
    ],
    "summarize": [
        """以下の文章を、専門外の人にも伝わる日本語の箇条書きに要約してください。

Multi-token prediction trains or packages a model so that it can predict more than one future
token at a time. During decoding, a lightweight draft path proposes multiple candidate tokens.
The target model then verifies those candidates in parallel. If several candidates are accepted,
the system advances multiple tokens with one expensive target-model pass. The speedup depends on
how predictable the task is, so coding, summarization, and rewriting often benefit more than
open-ended creative generation.""",
    ],
}


def list_prompt_sets() -> str:
    return ", ".join(sorted(PROMPT_SETS))


def get_prompts(name: str) -> list[str]:
    try:
        return PROMPT_SETS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown prompt set '{name}'. Choose one of: {list_prompt_sets()}"
        ) from exc
