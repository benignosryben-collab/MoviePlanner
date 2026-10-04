import math
from app import calculate_preferences, cosine_similarity, GENRES

def test_official_example():
    answers = {
        "q1": "exciting",
        "q2": "mystery",
        "q3": "dark",
        "q4": "intense",
        "q5": "surprised",
    }
    scores = calculate_preferences(answers)

    assert scores["Thriller"] == 13
    assert scores["Mystery"] == 10
    assert scores["Action"] == 5
    assert scores["Horror"] == 3
    assert scores["Adventure"] == 2
    assert scores["Sci-Fi"] == 2
    assert scores["Drama"] == 1
    assert scores["Comedy"] == 0
    assert scores["Romance"] == 0
    assert scores["Fantasy"] == 0

def test_exact_match():
    scores = {g: 0 for g in GENRES}
    scores["Action"] = 10
    assert math.isclose(cosine_similarity(scores, ["Action"]), 1.0)

def test_no_overlap():
    scores = {g: 0 for g in GENRES}
    scores["Action"] = 10
    assert math.isclose(cosine_similarity(scores, ["Fantasy"]), 0.0)

def test_relevant_genres_beat_unrelated_genres():
    scores = {g: 0 for g in GENRES}
    scores["Action"] = 10
    scores["Adventure"] = 7
    scores["Thriller"] = 5
    relevant = cosine_similarity(scores, ["Action", "Adventure", "Thriller"])
    unrelated = cosine_similarity(scores, ["Action", "Comedy"])
    assert relevant > unrelated

if __name__ == "__main__":
    test_official_example()
    test_exact_match()
    test_no_overlap()
    test_relevant_genres_beat_unrelated_genres()
    print("All Movie Planner logic tests passed.")
