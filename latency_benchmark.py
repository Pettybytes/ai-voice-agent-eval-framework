"""Latency benchmarking for voice AI systems"""

import time
import requests

def measure_tts_latency(text, api_key):
    """Measure time-to-first-audio for TTS"""
    
    start = time.time()
    
    response = requests.post(
        "https://api.elevenlabs.io/v1/text-to-speech/voice_id",
        headers={"xi-api-key": api_key},
        json={"text": text},
        stream=True
    )
    
    first_byte_time = None
    for chunk in response.iter_content(chunk_size=1024):
        if chunk and first_byte_time is None:
            first_byte_time = time.time() - start
            break
    
    return first_byte_time

def run_latency_tests(test_cases):
    """Run all latency benchmarks"""
    
    scores = []
    for test in test_cases:
        latency = measure_tts_latency(test["text"], test["api_key"])
        passed = latency < test["threshold_ms"] / 1000
        scores.append(100 if passed else 0)
    
    return sum(scores) / len(scores) if scores else 0
