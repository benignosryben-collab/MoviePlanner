# Movie Planner 🎬

A responsive movie recommendation web app built for an SIA1 project.

## What the project demonstrates

Movie Planner is **our own system** integrated with the existing TMDB API.

```text
User
 ↓
5-question questionnaire
 ↓
Our preference scoring
 ↓
Our recommendation algorithm
 ↓
TMDB API
 ↓
TMDB movie data
 ↓
Our matching + ranking
 ↓
Personalized recommendations
```

## Technology

- Python
- Flask
- HTML
- CSS
- JavaScript
- Requests
- TMDB API

## Setup

### 1. Install Python

Use Python 3.11+.

### 2. Open this folder in VS Code

Open the `MoviePlanner` folder.

### 3. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install packages

```bash
pip install -r requirements.txt
```

### 5. Create the environment file

Copy:

```text
.env.example
```

to:

```text
.env
```

Then add your TMDB credential.

Recommended:

```text
TMDB_ACCESS_TOKEN=YOUR_TMDB_API_READ_ACCESS_TOKEN
```

Or:

```text
TMDB_API_KEY=YOUR_TMDB_V3_API_KEY
```

Do NOT put the credential into `static/js/app.js`.

### 6. Run

```bash
python app.py
```

Open the local address shown by Flask, normally:

```text
http://127.0.0.1:5000
```

## Important

The `.env` file is ignored by Git because it contains your secret.

The current project uses TMDB's movie discovery endpoint and maps TMDB genre IDs into our 10 internal recommendation categories.

## Locked recommendation logic

The questionnaire and scoring table were designed separately from TMDB.

The Match % uses cosine similarity between:

1. The user's weighted preference vector.
2. The movie's 10-category genre-presence vector.

This means TMDB's rating is NOT the Match %.

Example:

```text
TMDB rating: 8.1
Movie Planner Match: 92.4%
```

The first is TMDB information. The second is our algorithm.

## TMDB attribution

This product uses the TMDB API but is not endorsed or certified by TMDB.

Movie data and images are provided by TMDB.

See TMDB's official documentation for current API terms and attribution requirements.
