def assess_risk():
    questions = [
        ("What is your investment horizon? (short/medium/long)", {"short": 1, "medium": 2, "long": 3}),
        ("How do you react to a 10% drop in value? (sell/hold/buy more)", {"sell": 1, "hold": 2, "buy more": 3}),
        ("What return range are you expecting annually? (low/medium/high)", {"low": 1, "medium": 2, "high": 3})
    ]
    score = 0
    for q, options in questions:
        ans = input(q + " ").strip().lower()
        score += options.get(ans, 2)
    return "Low" if score <= 4 else "Moderate" if score <= 6 else "High"