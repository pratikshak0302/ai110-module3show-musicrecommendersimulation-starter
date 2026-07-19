# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

These limitations were identified by inspecting `score_song` in `recommender.py` alongside the contents of `data/songs.csv`.

1. **Tiny, imbalanced catalog.** `songs.csv` holds only 10 songs, and genres are uneven — lofi appears 3 times while rock, jazz, ambient, synthwave, and indie pop appear once each. A rock or jazz listener effectively has one "correct" answer, so the recommender looks confident but has almost nothing to choose from. This is a **filter-bubble risk**: a listener is repeatedly funneled to the same one or two tracks.

2. **All-or-nothing categorical matching.** Genre and mood are scored by exact string equality (`_match`). "indie pop" earns zero genre credit against a "pop" preference even though they are musically adjacent, and "chill" gets nothing for a "relaxed" listener. The model cannot see that some genres/moods are neighbors, so it under-rewards close-but-not-exact matches.

3. **Energy dominates the numeric signal.** After renormalization, energy carries ~0.29 weight — nearly as much as an exact genre match. As shown in the experiment, this lets loud songs from the "wrong" genre climb into the top 5 (a rock fan sees pop tracks). The scoring can overfit to a single feature and quietly override genre intent.

4. **No content understanding.** The model never looks at lyrics, language, artist, era, or instrumentation. Two songs with identical numeric features are treated as interchangeable, so it cannot capture taste that depends on *what a song is about* or *who made it*.

5. **Popularity- and history-blind, and cold-start dependent.** There is no notion of listening history, novelty, or diversity in the final list — the same profile always yields the same ranking, and near-duplicate songs (e.g. two LoRoom lofi tracks) can both sit at the top. It also requires the user to state numeric preferences up front, which most real listeners cannot do accurately.

---

## 7. Evaluation  

**Profiles tested.** I evaluated three deliberately different listeners defined in `src/main.py` and ran them with `python -m src.main`:

- **High-Energy Pop** — pop, happy, energy 0.90, tempo 130
- **Chill Lofi** — lofi, chill, energy 0.38, tempo 75
- **Deep Intense Rock** — rock, intense, energy 0.90, tempo 150

**What I looked for.** For each profile I checked (a) whether the #1 pick actually matched the stated genre and mood, (b) whether the numeric explanations were consistent with the score, and (c) whether the ordering was sensible for that kind of listener.

**Observations.**

- The top pick was correct and intuitive for all three: Sunrise City (pop/happy), Library Rain and Midnight Coding (lofi/chill), and Storm Runner (rock/intense) each scored 0.94–0.98 by matching both genre and mood plus close energy.
- The Chill Lofi profile produced a two-way tie at 0.98 (Library Rain vs Midnight Coding) because their numeric features are nearly identical — the model has no tiebreaker beyond the raw score.
- What surprised me: cross-genre songs surfaced in the top 5 purely on energy. Storm Runner (rock) reached #4 for the pop listener and Sunrise City (pop) reached #4 for the rock listener. This is what motivated the weighting experiment.

**Comparisons I ran.** I compared the default weights against an energy-boosted / genre-reduced variant across all three profiles (documented in the README "Experiments You Tried" section). The comparison confirmed that energy weight controls how much genre boundaries are respected: raising it increased cross-genre diversity but weakened genre fidelity, while the Chill Lofi profile stayed stable because its genre and energy signals already agree.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
