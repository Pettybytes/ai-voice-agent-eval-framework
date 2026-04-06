"""Multi-turn dialogue testing"""

def test_context_retention(dialogue_history, expected_context):
    """Test if agent retains context across turns"""
    
    # Check if expected context appears in dialogue
    full_dialogue = " ".join([turn["text"] for turn in dialogue_history])
    
    retained_count = sum(1 for ctx in expected_context if ctx.lower() in full_dialogue.lower())
    
    return (retained_count / len(expected_context)) * 100 if expected_context else 0

def run_turn_tests(test_cases):
    """Run turn-taking evaluation"""
    
    scores = []
    for test in test_cases:
        score = test_context_retention(test["dialogue"], test["expected_context"])
        scores.append(score)
    
    return sum(scores) / len(scores) if scores else 0
