# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.
Modern music platforms such as Spotify and YouTube recommend songs by analyzing both user behavior and song characteristics. Many systems combine collaborative filtering, which learns from the listening habits of similar users, with content-based filtering, which compares song features like genre, mood, and energy to a user's preferences. This project implements a simplified content-based recommender. Each song is scored based on how closely its attributes match the user's preferred genre, mood, energy level, and tempo. Songs with the highest scores are ranked and recommended to the user.

Some prompts to answer:

- What features does each `Song` use in your system
Title
Artist
Genre
Mood
Energy
Tempo (BPM)

- What information does your `UserProfile` store
Preferred Genre
Preferred Mood
Preferred Energy
Preferred Tempo (BPM)
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

flowchart TD
    A[User Preferences] --> B[Load songs.csv]
    B --> C[Loop Through Each Song]
    
    C --> D[Compare Song Features]
    
    D --> E[Genre Similarity]
    D --> F[Mood Similarity]
    D --> G[Energy Similarity]
    D --> H[Tempo Similarity]
    D --> I[Danceability Similarity]
    D --> J[Valence Similarity]
    
    E --> K[Apply Feature Weights]
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L[Calculate Recommendation Score]
    L --> M[Store Song + Score]
    
    M --> N[Sort Scores Descending]
    N --> O[Return Top K Recommendations]

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Captured from `python -m src.main` (top 5 per profile).

**High-Energy Pop listener** — `genre=pop, mood=happy, energy=0.90, tempo=130, danceability=0.85, valence=0.80`

```
1. Sunrise City     - Neon Echo        Score: 0.94   (genre + mood match, energy 0.92)
2. Rooftop Lights   - Indigo Parade    Score: 0.82   (mood match, energy 0.86, danceability 0.97)
3. Gym Hero         - Max Pulse        Score: 0.78   (genre match, energy 0.97)
4. Storm Runner     - Voltline         Score: 0.57   (energy 0.99, no genre/mood match)
5. Night Drive Loop - Neon Echo        Score: 0.54   (energy 0.85, no genre/mood match)
```

**Chill Lofi listener** — `genre=lofi, mood=chill, energy=0.38, tempo=75, danceability=0.60, valence=0.58`

```
1. Library Rain        - Paper Lanterns  Score: 0.98   (genre + mood match, energy 0.97)
2. Midnight Coding     - LoRoom          Score: 0.98   (genre + mood match, energy 0.96)
3. Focus Flow          - LoRoom          Score: 0.79   (genre match, energy 0.98)
4. Spacewalk Thoughts  - Orbit Bloom     Score: 0.79   (mood match, energy 0.90)
5. Coffee Shop Stories - Slow Stereo     Score: 0.63   (energy 0.99, no genre/mood match)
```

**Deep Intense Rock listener** — `genre=rock, mood=intense, energy=0.90, tempo=150, danceability=0.60, valence=0.45`

```
1. Storm Runner     - Voltline        Score: 0.98   (genre + mood match, energy 0.99, tempo 0.97)
2. Gym Hero         - Max Pulse        Score: 0.75   (mood match, energy 0.97)
3. Night Drive Loop - Neon Echo        Score: 0.55   (energy 0.85, valence 0.96)
4. Sunrise City     - Neon Echo        Score: 0.52   (energy 0.92, no genre/mood match)
5. Rooftop Lights   - Indigo Parade    Score: 0.51   (energy 0.86, no genre/mood match)
```

### Why these songs ranked highly

- **Genre + mood match is the biggest lever.** Every #1 result (Sunrise City, Library Rain, Storm Runner) hits *both* the exact genre and exact mood, which contributes ~0.32 of the score before any numeric similarity is added. That combination is what separates a 0.94–0.98 top pick from the 0.5–0.8 mid-pack.
- **Energy is the strongest numeric feature** (weight ~0.29 after renormalization), so a song that matches neither genre nor mood can still crack the top 5 purely on energy — e.g. Storm Runner (a *rock* song) reaching #4 for the pop listener, and Sunrise City (a *pop* song) reaching #4 for the rock listener. Both share the ~0.90 target energy.
- **Ties are broken by the softer numeric features.** For the Chill Lofi listener, Library Rain and Midnight Coding both score 0.98; their near-identical danceability (0.98) and valence (0.98) similarity keep them locked together at the top.
- **The mid-pack is "one preference short."** Rooftop Lights ranks #2 for the pop listener on mood + strong numerics despite being *indie pop* (genre miss), while Gym Hero ranks high for the rock listener on mood + energy despite being *pop* (genre miss). Missing a single categorical match costs roughly one rank.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Experiment: boost energy, shrink genre

**Change made:** I doubled the weight on `energy` (0.15 → 0.30) and halved the weight on `genre` (0.25 → 0.125), then renormalized all six weights so they still sum to 1.0. This lives in `score_song` in [recommender.py:152-160](src/recommender.py#L152-L160). The intent was to test whether "how the song *feels* energy-wise" should outrank "is it my genre."

**How I measured impact:** I re-ran all three profiles under the original (baseline) weights and under the new weights and compared the top-5 rankings.

| Profile | Baseline top 5 | Experiment top 5 | What moved |
|---------|----------------|------------------|-----------|
| High-Energy Pop | Sunrise, Gym Hero, Rooftop, Storm Runner, Night Drive | Sunrise, **Rooftop**, Gym Hero, Storm Runner, Night Drive | Rooftop (indie pop) jumped above Gym Hero; Storm Runner rose 0.44 → 0.57 |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow, Spacewalk, Coffee Shop | *unchanged order* | Coffee Shop rose 0.50 → 0.63 but stayed #5 |
| Deep Intense Rock | Storm Runner, Gym Hero, Night Drive, Rooftop, Sunrise | Storm Runner, Gym Hero, Night Drive, **Sunrise**, Rooftop | Sunrise (pop) climbed above Rooftop; all high-energy non-rock songs rose |

**Takeaway:** Raising the energy weight lets high-energy songs from *other* genres climb the list — it makes recommendations more diverse and less genre-locked. The cost is weaker genre fidelity: a rock fan starts seeing pop and synthwave in their top 5 simply because those tracks are also loud and fast. Profiles whose genre and energy already agree (Chill Lofi) barely change, because both signals point at the same songs.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



