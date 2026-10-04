import math
import os
from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# TMDB movie genre IDs -> Movie Planner's 10 internal categories.
GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    35: "Comedy",
    18: "Drama",
    27: "Horror",
    9648: "Mystery",
    10749: "Romance",
    878: "Sci-Fi",
    53: "Thriller",
    14: "Fantasy",
}

GENRES = list(GENRE_MAP.values())

# Locked questionnaire scoring.
SCORING = {
    "q1": {
        "fun": {"Comedy": 3, "Adventure": 2, "Fantasy": 1, "Romance": 1},
        "exciting": {"Action": 3, "Adventure": 2, "Thriller": 2, "Sci-Fi": 1},
        "thinking": {"Mystery": 3, "Thriller": 2, "Sci-Fi": 2, "Drama": 1},
        "emotional": {"Drama": 3, "Romance": 2, "Adventure": 1},
        "scared": {"Horror": 3, "Thriller": 3, "Mystery": 1},
    },
    "q2": {
        "adventure": {"Adventure": 4, "Action": 2, "Fantasy": 1, "Sci-Fi": 1},
        "action": {"Action": 4, "Thriller": 2, "Adventure": 1},
        "mystery": {"Mystery": 4, "Thriller": 2, "Drama": 1},
        "romance": {"Romance": 4, "Drama": 2, "Comedy": 1},
        "scary": {"Horror": 4, "Thriller": 3, "Mystery": 1},
        "scifi": {"Sci-Fi": 4, "Adventure": 2, "Action": 1},
    },
    "q3": {
        "light": {"Comedy": 3, "Adventure": 1, "Romance": 1, "Fantasy": 1},
        "fast": {"Action": 3, "Thriller": 2, "Adventure": 1},
        "dark": {"Mystery": 3, "Thriller": 3, "Horror": 1},
        "serious": {"Drama": 3, "Romance": 1, "Thriller": 1},
        "fantastical": {"Fantasy": 3, "Adventure": 2, "Sci-Fi": 1},
        "grounded": {"Drama": 3, "Thriller": 1, "Romance": 1},
    },
    "q4": {
        "chill": {"Comedy": 2, "Romance": 1, "Drama": 1},
        "moderate": {"Drama": 1, "Adventure": 1, "Comedy": 1},
        "exciting": {"Action": 2, "Adventure": 2, "Thriller": 1},
        "intense": {"Action": 2, "Thriller": 3, "Horror": 2},
        "disturbing": {"Horror": 4, "Thriller": 3},
    },
    "q5": {
        "hilarious": {"Comedy": 4, "Romance": 1, "Adventure": 1},
        "surprised": {"Thriller": 3, "Mystery": 3, "Sci-Fi": 1},
        "feel": {"Drama": 4, "Romance": 2},
        "adventure": {"Adventure": 4, "Action": 2, "Fantasy": 1},
        "think": {"Mystery": 3, "Sci-Fi": 2, "Drama": 2, "Thriller": 1},
        "terrifying": {"Horror": 4, "Thriller": 3},
        "action": {"Action": 4, "Adventure": 2, "Thriller": 1},
    },
}


def blank_scores():
    return {genre: 0 for genre in GENRES}


def calculate_preferences(answers):
    scores = blank_scores()
    for question in ("q1", "q2", "q3", "q4", "q5"):
        answer = answers.get(question)
        if answer not in SCORING[question]:
            raise ValueError(f"Invalid answer for {question}.")
        for genre, points in SCORING[question][answer].items():
            scores[genre] += points
    return scores


def cosine_similarity(user_scores, movie_genres):
    movie_set = set(movie_genres)
    dot = sum(user_scores[g] * (1 if g in movie_set else 0) for g in GENRES)
    user_norm = math.sqrt(sum(user_scores[g] ** 2 for g in GENRES))
    movie_norm = math.sqrt(sum((1 if g in movie_set else 0) ** 2 for g in GENRES))

    if user_norm == 0 or movie_norm == 0:
        return 0.0

    return dot / (user_norm * movie_norm)


def why_movie(user_scores, movie_genres):
    matched = [g for g in GENRES if g in movie_genres and user_scores[g] > 0]
    matched.sort(key=lambda g: user_scores[g], reverse=True)

    if not matched:
        return "This movie has no direct genre overlap with your selected preferences."

    top = matched[:3]
    if len(top) == 1:
        return f"This movie matches your interest in {top[0]}."
    if len(top) == 2:
        return f"This movie matches your strong interest in {top[0]} and {top[1]}."
    return f"This movie matches your strong interest in {top[0]}, {top[1]}, and {top[2]}."


def format_movie(movie, user_scores):
    genre_names = [GENRE_MAP[g] for g in movie.get("genre_ids", []) if g in GENRE_MAP]
    score = cosine_similarity(user_scores, genre_names)
    release_date = movie.get("release_date") or ""
    year = release_date[:4] if release_date else "N/A"

    poster_path = movie.get("poster_path")
    poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None

    return {
        "id": movie.get("id"),
        "title": movie.get("title") or "Untitled",
        "overview": movie.get("overview") or "No overview is available for this movie.",
        "release_year": year,
        "rating": round(float(movie.get("vote_average") or 0), 1),
        "genres": genre_names,
        "poster_url": poster_url,
        "match": round(score * 100, 1),
        "why": why_movie(user_scores, genre_names),
    }


def tmdb_request(params):
    token = os.getenv("TMDB_ACCESS_TOKEN", "").strip()
    api_key = os.getenv("TMDB_API_KEY", "").strip()

    if not token and not api_key:
        raise RuntimeError(
            "TMDB credentials are missing. Add TMDB_ACCESS_TOKEN or TMDB_API_KEY to your .env file."
        )

    headers = {"accept": "application/json"}
    query = dict(params)

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if api_key:
        query["api_key"] = api_key

    response = requests.get(
        f"{TMDB_BASE_URL}/discover/movie",
        params=query,
        headers=headers,
        timeout=10,
    )

    if response.status_code == 401:
        raise RuntimeError("TMDB authentication failed. Check your API credentials.")
    if response.status_code == 429:
        raise RuntimeError("TMDB rate limit reached. Please wait and try again.")
    if response.status_code >= 500:
        raise RuntimeError("TMDB is temporarily unavailable. Please try again later.")
    response.raise_for_status()

    return response.json()


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/recommend")
def recommend():
    try:
        payload = request.get_json(silent=True) or {}
        answers = payload.get("answers", {})
        user_scores = calculate_preferences(answers)

        # Query several pages from TMDB using the user's strongest internal genres.
        # TMDB's with_genres is used only to build a relevant candidate pool.
        # Our own cosine algorithm still determines the final ranking.
        strongest = sorted(
            [g for g, score in user_scores.items() if score > 0],
            key=lambda g: user_scores[g],
            reverse=True,
        )[:3]

        internal_to_tmdb = {name: tmdb_id for tmdb_id, name in GENRE_MAP.items()}
        genre_ids = [str(internal_to_tmdb[g]) for g in strongest]

        all_movies = []
        for page in (1, 2):
            data = tmdb_request({
                "language": "en-US",
                "include_adult": "false",
                "include_video": "false",
                "sort_by": "popularity.desc",
                "page": page,
                "with_genres": "|".join(genre_ids),
            })
            all_movies.extend(data.get("results", []))

        # Remove duplicate movie IDs.
        unique = {}
        for movie in all_movies:
            if movie.get("id") is not None:
                unique[movie["id"]] = movie

        recommendations = [
            format_movie(movie, user_scores)
            for movie in unique.values()
            if any(g in GENRE_MAP for g in movie.get("genre_ids", []))
        ]

        recommendations.sort(
            key=lambda m: (m["match"], m["rating"]),
            reverse=True,
        )

        # Avoid overwhelming the user.
        recommendations = recommendations[:8]

        if not recommendations:
            return jsonify({
                "success": False,
                "message": "No matching movies were found. Please try a different set of answers."
            }), 404

        strongest_preferences = sorted(
            user_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:3]

        return jsonify({
            "success": True,
            "preferences": [
                {"genre": genre, "score": score}
                for genre, score in strongest_preferences
            ],
            "recommendations": recommendations,
        })

    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except requests.RequestException:
        return jsonify({
            "success": False,
            "message": "The movie service could not be reached. Check your internet connection and try again."
        }), 502
    except RuntimeError as exc:
        return jsonify({"success": False, "message": str(exc)}), 502
    except Exception:
        app.logger.exception("Unexpected error")
        return jsonify({
            "success": False,
            "message": "Something unexpected happened. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
