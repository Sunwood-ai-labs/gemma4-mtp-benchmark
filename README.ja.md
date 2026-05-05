<div align="center">

# Gemma 4 MTP Benchmark

Gemma 4 LiteRT-LM の Multi-Token Prediction オン/オフ差を、Apple Silicon Mac で体感するための小さな公開ベンチです。

[English](README.md) | [Docs](https://sunwood-ai-labs.github.io/gemma4-mtp-benchmark/)

[![CI](https://github.com/Sunwood-ai-labs/gemma4-mtp-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/Sunwood-ai-labs/gemma4-mtp-benchmark/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-3776ab.svg)](pyproject.toml)

</div>

## 何を体験できるか

Google の LiteRT-LM Gemma 4 ページでは、現時点で E2B/E4B が LiteRT-LM 対応で、GPUバックエンドではMTPが推奨されています。このリポジトリは、その差をローカルMacで手元確認するための再現用ベンチです。

測るもの:

- speculative decoding なしの通常生成
- speculative decoding ありの MTP 生成
- 生成秒数、chars/sec、推定 tokens/sec
- Macの機種、チップ、メモリなどの実行環境

モデルファイルは実行時にHugging Faceキャッシュへダウンロードします。リポジトリには入りません。

## 動画で見る

ローカル M1 Max のタスクマトリクスをもとに、30秒の HyperFrames 動画も入れています。

[速度比較動画を見る](https://sunwood-ai-labs.github.io/gemma4-mtp-benchmark/assets/mtp-speed-comparison.mp4)

E4B coding の `76.28s` 対 `40.79s` をバーで見せつつ、coding / JSON / extract では差が出やすく、creative や短い quick では横ばいまたは遅くなる場合がある、という傾向まで見えるようにしています。

## まず動かす

Apple Silicon Mac なら `uv` 利用が一番ラクです。

```bash
git clone https://github.com/Sunwood-ai-labs/gemma4-mtp-benchmark.git
cd gemma4-mtp-benchmark
uv venv
uv pip install -e '.[bench]'
uv run gemma4-mtp-bench doctor
```

E2Bで軽く比較:

```bash
uv run gemma4-mtp-bench run \
  --model e2b \
  --backend gpu \
  --prompt-set quick \
  --rounds 1 \
  --output results/e2b-gpu-quick.json
```

16GB以上のMacなら、E4Bのコード生成ベンチが体感差を見やすいです。

```bash
uv run gemma4-mtp-bench run \
  --model e4b \
  --backend gpu \
  --prompt-set coding \
  --rounds 2 \
  --output results/e4b-gpu-coding.json
```

このリポジトリ作成時に MacBook Pro M1 Max / 64 GB で実測したところ、E4B GPU のコード生成では MTP ありがおよそ `1.87x` の推定 tokens/sec になりました。一方、短いE2B quickプロンプトではこの1回の実測だとMTPありのほうが遅く出たため、`quick` は動作確認用、体感比較は `coding` または `summarize` がおすすめです。詳細は [local benchmark note](benchmarks/2026-05-06-m1-max.md) に残しています。

同じ M1 Max で複数タスクを1回ずつ回したところ、MTPの差が出やすいのは予測しやすいタスクでした。

- E4B GPU `coding`: `1.87x`
- E4B GPU `json`: `1.65x`
- E4B GPU `extract`: `1.51x`
- E2B GPU `json`: `1.53x`
- E2B CPU `json`: `1.81x`

逆に、自由度が高い `creative` や短い `quick` は横ばいか遅めでした。詳細は [task matrix note](benchmarks/2026-05-06-task-matrix-m1-max.md) に残しています。

結果をMarkdownにします。

```bash
uv run gemma4-mtp-bench report \
  results/e4b-gpu-coding.json \
  --output results/e4b-gpu-coding.md
```

## おすすめ設定

| Mac | 最初に試す設定 |
| --- | --- |
| M1/M2/M3/M4、8GB | `--model e2b --backend gpu --prompt-set quick` |
| M1/M2/M3/M4、16GB以上 | `--model e4b --backend gpu --prompt-set coding` |
| M4 Pro/Max/Ultra | `--model e4b --backend gpu --prompt-set coding --rounds 3` |
| Intel Mac | CPU実行は試せますが、今回のMTP体感目的では主対象ではありません |

プロンプトセット:

- `quick`: 短い日本語説明
- `coding`: Pythonコード生成。MTP差を見やすいです
- `summarize`: 要約タスク
- `rewrite`: README向けのリライト
- `extract`: ログからの構造化抽出
- `json`: JSON形式への整形
- `translation`: 技術文の英日翻訳
- `creative`: 短い自由導入文

複数タスクをまとめて試す:

```bash
scripts/run-gpu-task-matrix.sh e4b gpu 1 1
```

## 結果の見方

出力はこのような表になります。

```text
| MTP | runs | mean seconds | mean chars/sec | est tokens/sec |
| --- | ---: | ---: | ---: | ---: |
| off | 2 | 18.42 | 49.1 | 18.0 |
| on  | 2 | 10.21 | 88.4 | 32.2 |

Estimated MTP speed ratio: 1.79x
```

`est tokens/sec` は出力文字数からの推定です。LiteRT-LM の簡易ストリーミングAPIでは正確なトークン数を受け取らないため、同じプロンプトセット同士で比較してください。

## うまくいかない時

GPUで失敗したら、まずCPUで通るか見ます。

```bash
uv run gemma4-mtp-bench run --model e2b --backend cpu --prompt-set quick --rounds 1
```

LiteRT/WebGPU がアダプタやカーネル初期化の低レベルログを表示することがあります。コマンドがエラー終了していなければ、基本的には通常ログとして扱ってください。

2026-05-05より前にLiteRT版Gemma 4モデルをダウンロードしていた場合、speculative decodingを使うには再ダウンロードが推奨されています。古いHugging Faceキャッシュを削除してから再実行してください。

## 参考

- [Google AI Edge: Gemma 4 for LiteRT-LM](https://ai.google.dev/edge/litert-lm/models/gemma-4)
- [Google AI Edge: LiteRT-LM CLI](https://ai.google.dev/edge/litert-lm/cli)
- [Google AI Edge: LiteRT-LM Python API](https://ai.google.dev/edge/litert-lm/python)
- [Hugging Face: Gemma 4 E2B LiteRT-LM](https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm)
- [Hugging Face: Gemma 4 E4B LiteRT-LM](https://huggingface.co/litert-community/gemma-4-E4B-it-litert-lm)

## ライセンス

リポジトリのコードとドキュメントは Apache-2.0 です。Gemmaモデル重みはHugging Faceから取得され、各モデル側の条件に従います。
