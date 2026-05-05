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
    "rewrite": [
        """次の文章を、GitHub READMEの説明として自然な日本語にリライトしてください。
条件:
- 300字以内
- 箇条書きを3つ含める
- 読者がすぐ試したくなるトーン

原文:
Gemma 4のMTPをローカルMacで確認する。普通の生成とMTPあり生成を同じプロンプトで比較する。
E2BとE4Bを選べる。結果はJSONに保存する。速いかどうかはタスクによって変わる。""",
    ],
    "extract": [
        """次のログから、重要な情報だけを日本語で整理してください。
出力は「環境」「結果」「注意」の3見出しにしてください。

LOG:
device=MacBook Pro
chip=Apple M1 Max
memory=64GB
model=Gemma 4 E4B
backend=gpu
task=coding
baseline_seconds=76.28
mtp_seconds=40.79
estimated_ratio=1.87
note=short freeform prompt did not improve on E2B""",
    ],
    "json": [
        """以下のベンチ結果をJSONだけに変換してください。
キーは model, backend, task, baseline_seconds, mtp_seconds, speed_ratio, conclusion にしてください。
conclusion は短い日本語文字列にしてください。

Model: Gemma 4 E4B
Backend: GPU
Task: coding
Baseline: 76.28 seconds
MTP: 40.79 seconds
Ratio: 1.87x
Conclusion: コード生成ではMTPの体感差が大きい""",
    ],
    "translation": [
        """次の英語説明を、技術ブログ向けの自然な日本語に翻訳してください。
出力は400字以内にしてください。

Multi-token prediction can make local language model decoding feel faster by proposing several
future tokens at once. The main model verifies those candidates in parallel. When the task is
predictable, such as code generation, rewriting, or summarization, more proposed tokens are
accepted and the response advances faster.""",
    ],
    "creative": [
        """「ローカルLLMの速度比較を初めて試す開発者」に向けて、短い導入文を書いてください。
条件:
- 500字以内
- 比喩は1つまで
- 技術的に断定しすぎない
- 最後に試すべきコマンドの種類を1つ示す""",
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
