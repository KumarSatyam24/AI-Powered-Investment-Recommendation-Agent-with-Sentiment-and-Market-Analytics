def generate_recommendation(sentiment, risk):
    if sentiment == "Positive":
        return "Buy" if risk != "Low" else "Hold"
    elif sentiment == "Negative":
        return "Sell" if risk != "High" else "Hold"
    else:
        return "Hold"