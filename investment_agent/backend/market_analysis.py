def analyze_market(index_data, vix, inflation):
    if vix > 25 or inflation > 5:
        return "Risk-Off"
    return "Risk-On"