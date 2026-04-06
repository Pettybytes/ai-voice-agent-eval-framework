# AI Voice Agent Evaluation Framework

**Production evaluation framework for voice AI systems**

Latency benchmarks, NLP accuracy scoring, turn-taking tests, regression detection.

## Why Evaluation Matters

In production voice AI, milliseconds matter. This framework ensures:
- Response latency stays under threshold
- NLP accuracy doesn't regress
- Multi-turn dialogue works correctly

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python eval_runner.py --test-set test_cases/sample_eval_set.json
```

## 📊 What Gets Tested

- **Latency**: Time-to-first-audio, end-to-end response
- **Accuracy**: NLP output vs. ground truth
- **Turn-taking**: Multi-turn context retention

See individual modules for details.
