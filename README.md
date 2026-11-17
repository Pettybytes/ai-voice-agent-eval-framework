# Voice Agent Evaluation & Tuning

Measure what the caller experiences, verify what the agent does, and reject faster configurations that break the task.

A dependency-free Python harness for captured voice-agent observations, with an opt-in ElevenLabs transport probe. Includes deterministic task contracts, assistant-only context checks, ASR word error rate, playback/interrupt timing, retrieval scoring, regression gates, and tuning against a held-out split.

**Status:** checked-in examples are explicitly synthetic. They demonstrate the evaluator, not production latency, a deployed Kong integration, or a model's real-world accuracy. Real measurements require instrumented application captures. This project replaces the earlier illustrative word-overlap and conversation-keyword checks.

## Run locally

Python 3.10+, no packages or API keys needed:

```bash
python -m unittest discover -s tests -v
python eval_runner.py --test-set test_cases/sample_eval_set.json --report reports/sample.json
python tune.py --experiments test_cases/tuning_example.json --report reports/tuning.json
python tune.py --grid configs/tuning_grid.json --report reports/plan.json
```

Verify that a bad agent cannot get a green report:

```bash
python eval_runner.py --test-set test_cases/failing_eval_set.json
# Exit 1: deliberately incorrect observations.
```

Exit codes: **0** all required checks passed; **1** measured gate failure; **2** invalid input. Missing required sections fail; empty suites and malformed traces are rejected. Reports preserve individual failures rather than averaging them away.

## What changed and why

| Original problem | Replacement | Limit of the measurement |
| --- | --- | --- |
| Literal `voice_id` in URL; buffered first chunk | Configured voice on the streaming endpoint; monotonic first-byte and full-body timing | Received audio bytes do not prove playback or intelligibility |
| Word overlap called “accuracy” | Exact structured intent/slot/action/outcome contracts; separate Levenshtein WER | Structured correctness is not a general semantic judge |
| User's words could pass context recall | Check only the designated assistant probe, including corrected facts | Requires captured structured output or independently reviewed annotation |
| No measured interruption behavior | Speech/playback timestamps, interruption stop, cancellation acknowledgement and recovery | Requires playback-sink events from one clock; does not synthesize them |
| No tuning discipline | Parameter grid, quality gates, calibration ranking, winner-only holdout | Replays captures; does not apply provider configuration or run a live sweep |

## Measurements

- **Response latency:** actual user speech end → assistant playback start; p50/p95/count/max.
- **Barge-in stop:** interrupting user speech start → prior assistant playback stop. Cancellation acknowledgement is reported separately.
- **Recovery:** interrupting speech end → next assistant playback start. Missing events, unannotated overlaps, and overlapping assistant audio cannot silently pass.
- **Stage timing:** optional adjacent STT/model/TTS markers. Absent stages stay absent.
- **Named timing:** explicit application metrics such as end-of-speech *decision* → playback, with separate labels and thresholds.
- **Task correctness/context:** exact captured JSON fields; no substring scoring or hidden LLM judge.
- **ASR WER:** token edit distance, including insertions/deletions/substitutions; may exceed 100%.
- **RAG:** recall@k, precision@k, MRR@k and citation membership. These do **not** establish that a cited passage entails the answer.

See [capture contract](docs/capture-contract.md), [tuning workflow](docs/tuning.md), and [latency and component rationale](docs/latency-and-components.md).

## Regression checks

```bash
python eval_runner.py --test-set test_cases/sample_eval_set.json \
  --baseline reports/sample.json --max-p95-regression-ms 100 \
  --report reports/comparison.json
```

Baseline comparisons require identical benchmark contracts, source labels and sample counts. Every current quality gate must still pass. Percentiles use nearest rank; a p95 from two samples is simply the maximum, not convincing tail-latency evidence.

## Live TTS probe (optional)

Export `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` through your shell's secret mechanism, then:

```bash
python latency_benchmark.py --live --runs 5 --model-id eleven_flash_v2_5
```

This makes billable requests. No `.env` auto-loading, automatic retries or calls during tests. Voice IDs must be real; errors, empty streams, redirects and non-audio responses are rejected. It reports **first audio byte received**, not time-to-audible-speech. The socket timeout and between-read elapsed budget are documented in the function.

## RAG and caching

[Kong integration options](docs/kong-rag-and-caching.md) distinguish AI RAG Injector, AI Semantic Cache and schema caching. Kong deployment remains an optional integration plan; this repository does not install or configure a gateway.

`schema_cache.py` provides a bounded local schema cache keyed by trusted scope, schema name and revision, with TTL, invalidation and defensive copies. It is independent of answer caching and does not change any application's authorization.
