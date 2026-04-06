#!/usr/bin/env python3
"""Main evaluation runner"""

import json
import sys
from latency_benchmark import run_latency_tests
from nlp_accuracy import run_accuracy_tests
from turn_taking_tests import run_turn_tests

def main(test_file="test_cases/sample_eval_set.json"):
    """Run all evaluations"""
    
    with open(test_file) as f:
        test_data = json.load(f)
    
    print("🧪 Running Voice AI Evaluation Suite")
    print("=" * 50)
    
    latency_score = run_latency_tests(test_data["latency_tests"])
    accuracy_score = run_accuracy_tests(test_data["accuracy_tests"])
    turn_score = run_turn_tests(test_data["turn_tests"])
    
    print(f"\n📊 Results:")
    print(f"  Latency: {latency_score:.1f}%")
    print(f"  Accuracy: {accuracy_score:.1f}%")
    print(f"  Turn-taking: {turn_score:.1f}%")
    
    overall = (latency_score + accuracy_score + turn_score) / 3
    print(f"\n  Overall: {overall:.1f}%")
    
    return overall >= 90.0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
