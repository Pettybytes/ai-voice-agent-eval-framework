"""NLP accuracy scoring against ground truth"""

def calculate_accuracy(predicted, expected):
    """Compare predicted output to ground truth"""
    
    # Simple word overlap for demo
    pred_words = set(predicted.lower().split())
    exp_words = set(expected.lower().split())
    
    if not exp_words:
        return 100.0
    
    overlap = len(pred_words & exp_words)
    accuracy = (overlap / len(exp_words)) * 100
    
    return min(accuracy, 100.0)

def run_accuracy_tests(test_cases):
    """Run NLP accuracy evaluation"""
    
    scores = []
    for test in test_cases:
        accuracy = calculate_accuracy(test["predicted"], test["expected"])
        scores.append(accuracy)
    
    return sum(scores) / len(scores) if scores else 0
