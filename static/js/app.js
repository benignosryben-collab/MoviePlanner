const questions = [
    {
        id: "q1",
        title: "What's your mood right now?",
        hint: "Pick the feeling you want your movie to match.",
        options: [
            ["fun", "😄", "Fun and light"],
            ["exciting", "🔥", "Exciting"],
            ["thinking", "🧠", "Makes me think"],
            ["emotional", "🥹", "Emotional"],
            ["scared", "😨", "Scared or tense"]
        ]
    },
    {
        id: "q2",
        title: "What kind of experience do you want?",
        hint: "Choose the type of story or experience you're looking for.",
        options: [
            ["adventure", "🗺️", "Adventure/exploration"],
            ["action", "💥", "Action/intense moments"],
            ["mystery", "🕵️", "Mystery/figure something out"],
            ["romance", "❤️", "Relationships/romance"],
            ["scary", "👻", "Dark/scary"],
            ["scifi", "🚀", "Science/space/futuristic"]
        ]
    },
    {
        id: "q3",
        title: "What kind of movie atmosphere do you want?",
        hint: "Think about the overall vibe, not just the plot.",
        options: [
            ["light", "☀️", "Light and cheerful"],
            ["fast", "⚡", "Fast-paced and energetic"],
            ["dark", "🌑", "Dark and mysterious"],
            ["serious", "💙", "Emotional and serious"],
            ["fantastical", "✨", "Imaginative and fantastical"],
            ["grounded", "🎭", "Realistic and grounded"]
        ]
    },
    {
        id: "q4",
        title: "How intense do you want the movie to be?",
        hint: "Choose the level of intensity you want tonight.",
        options: [
            ["chill", "🌿", "Chill/relaxing"],
            ["moderate", "🙂", "Moderate"],
            ["exciting", "⚡", "Exciting"],
            ["intense", "🔥", "Very intense/stressful"],
            ["disturbing", "😱", "Disturbing/scary"]
        ]
    },
    {
        id: "q5",
        title: 'What would make you say "that was a good movie"?',
        hint: "Pick the payoff you want from the movie.",
        options: [
            ["hilarious", "😂", "That was hilarious."],
            ["surprised", "🤯", "That completely surprised me."],
            ["feel", "❤️", "That really made me feel something."],
            ["adventure", "🗺️", "That was an amazing adventure."],
            ["think", "🧠", "That made me think afterward."],
            ["terrifying", "😱", "That was terrifying!"],
            ["action", "💥", "The action was incredible."]
        ]
    }
];

let current = 0;
const answers = {};

const hero = document.getElementById("hero");
const quiz = document.getElementById("quiz");
const loading = document.getElementById("loading");
const results = document.getElementById("results");
const questionTitle = document.getElementById("questionTitle");
const questionHint = document.getElementById("questionHint");
const progressText = document.getElementById("progressText");
const progressBar = document.getElementById("progressBar");
const options = document.getElementById("options");
const backBtn = document.getElementById("backBtn");
const nextBtn = document.getElementById("nextBtn");
const movieGrid = document.getElementById("movieGrid");
const preferenceSummary = document.getElementById("preferenceSummary");
const errorBox = document.getElementById("errorBox");

document.getElementById("startBtn").addEventListener("click", () => {
    hero.classList.add("hidden");
    quiz.classList.remove("hidden");
    current = 0;
    renderQuestion();
    window.scrollTo({top: 0, behavior: "smooth"});
});

function renderQuestion() {
    const q = questions[current];
    questionTitle.textContent = q.title;
    questionHint.textContent = q.hint;
    progressText.textContent = `${current + 1} / ${questions.length}`;
    progressBar.style.width = `${((current + 1) / questions.length) * 100}%`;

    options.innerHTML = "";

    q.options.forEach(([value, emoji, label]) => {
        const button = document.createElement("button");
        button.className = "option";
        if (answers[q.id] === value) button.classList.add("selected");

        button.innerHTML = `<span class="emoji">${emoji}</span>${label}`;
        button.addEventListener("click", () => {
            answers[q.id] = value;
            renderQuestion();
        });
        options.appendChild(button);
    });

    backBtn.disabled = current === 0;
    nextBtn.disabled = !answers[q.id];
    nextBtn.textContent = current === questions.length - 1 ? "Find My Movies →" : "Next →";
}

backBtn.addEventListener("click", () => {
    if (current > 0) {
        current--;
        renderQuestion();
    }
});

nextBtn.addEventListener("click", async () => {
    if (!answers[questions[current].id]) return;

    if (current < questions.length - 1) {
        current++;
        renderQuestion();
        return;
    }

    await getRecommendations();
});

document.getElementById("againBtn").addEventListener("click", () => {
    Object.keys(answers).forEach(key => delete answers[key]);
    current = 0;
    results.classList.add("hidden");
    quiz.classList.remove("hidden");
    renderQuestion();
    window.scrollTo({top: 0, behavior: "smooth"});
});

async function getRecommendations() {
    quiz.classList.add("hidden");
    loading.classList.remove("hidden");
    errorBox.classList.add("hidden");
    window.scrollTo({top: 0, behavior: "smooth"});

    try {
        const response = await fetch("/api/recommend", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({answers})
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Unable to get recommendations.");
        }

        renderResults(data);
    } catch (error) {
        loading.classList.add("hidden");
        quiz.classList.remove("hidden");
        errorBox.textContent = error.message;
        errorBox.classList.remove("hidden");
        window.scrollTo({top: 0, behavior: "smooth"});
    }
}

function renderResults(data) {
    loading.classList.add("hidden");
    results.classList.remove("hidden");

    const prefs = data.preferences
        .map(item => `${item.genre} (${item.score})`)
        .join(" · ");

    preferenceSummary.textContent = `Your strongest preferences: ${prefs}`;

    movieGrid.innerHTML = data.recommendations.map(movie => {
        const poster = movie.poster_url
            ? `<img src="${escapeHtml(movie.poster_url)}" alt="${escapeHtml(movie.title)} poster" loading="lazy">`
            : `<div class="poster-fallback">🎬</div>`;

        const tags = movie.genres
            .map(g => `<span class="tag">${escapeHtml(g)}</span>`)
            .join("");

        return `
            <article class="movie-card">
                <div class="poster-wrap">
                    ${poster}
                    <span class="match">${movie.match}% Match</span>
                </div>
                <div class="movie-body">
                    <h3 class="movie-title">${escapeHtml(movie.title)}</h3>
                    <div class="meta">${escapeHtml(movie.release_year)} · TMDB ★ ${movie.rating}</div>
                    <div class="tags">${tags}</div>
                    <p class="overview">${escapeHtml(movie.overview)}</p>
                    <p class="why"><strong>Why this movie?</strong><br>${escapeHtml(movie.why)}</p>
                </div>
            </article>
        `;
    }).join("");

    window.scrollTo({top: 0, behavior: "smooth"});
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
