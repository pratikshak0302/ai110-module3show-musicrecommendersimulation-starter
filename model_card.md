# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0** — a content-based music recommender simulation.

---

## 2. Intended Use  

**Goal / task.** VibeMatch takes a listener's stated taste (a preferred genre, mood, and target values for energy, tempo, danceability, and valence) and returns a ranked list of songs from a small catalog, each with a short reason for its score. It answers one question: *"given what you say you like, which songs in this catalog fit best?"*

**Assumptions about the user.** It assumes the listener can describe their taste as explicit preferences up front, and that a good recommendation is simply the song whose features are closest to those preferences.

**Intended use.** This is a **classroom / learning tool**. It exists to demonstrate how content-based filtering turns song features and user preferences into a score, and to make the scoring transparent enough to inspect and experiment with.

**Non-intended use.** It is **not** built for real listeners or production use. It should not be used to make actual music-discovery decisions, to compare or rank real artists, or in any setting where its output affects what real people hear — the catalog is tiny, the scoring is deliberately simple, and it has no listening history, personalization, or fairness safeguards.

---

## 3. How the Model Works  

Think of it like a checklist scored against your taste. You describe what you want — a genre, a mood, and roughly how energetic, fast, danceable, and upbeat the music should be. The model then walks through every song in the catalog and asks, feature by feature, "how close is this song to what you asked for?"

For genre and mood it's all-or-nothing: the song either matches your pick or it doesn't. For the number-based features (energy, tempo, danceability, valence) it gives partial credit — the closer the song's value is to your target, the more points it earns for that feature.

Not every feature counts equally. Each one has a **weight** that says how much it matters, and the model adds up the weighted points into a single score between 0 and 1. Songs are then sorted from highest to lowest, and the top few are shown to you along with a plain-language reason for each.

**What changed from the starter logic:** I expanded the score to use six features instead of just a couple, made the numeric features award partial credit for "close enough" instead of exact matches, and ran a weighting experiment that increased the importance of energy and reduced the importance of genre (see the README experiment and §6).

---

## 4. Data  

The catalog lives in `data/songs.csv` and holds **10 songs**. Each song has a title, artist, and six taste features: genre, mood, energy, tempo (BPM), valence, danceability, and acousticness.

**Genres represented:** pop, lofi (×3), rock, ambient, jazz, synthwave, indie pop. **Moods represented:** happy, chill, intense, relaxed, focused, moody.

I did not add or remove songs — the recommender is built and evaluated on the provided starter dataset.

**What's missing:** the catalog is small and uneven — lofi is over-represented while most other genres appear only once. Whole swaths of musical taste are absent (hip-hop, classical, country, metal, electronic subgenres, non-English music), and there is no data on lyrics, language, era, or popularity. This limits how meaningfully the model can serve any listener whose taste falls outside the handful of genres present.

---

## 5. Strengths  

- **Transparent and explainable.** Every recommendation comes with a per-feature breakdown, so it is always clear *why* a song ranked where it did — a real advantage over black-box recommenders.
- **Works well for clearly-defined tastes.** When a listener's genre, mood, and energy all point the same direction (e.g. the Chill Lofi profile), the top picks are intuitive and score very high (0.98).
- **Captures "close enough" sensibly.** Partial credit on numeric features means a song that's slightly off-target still competes, matching the intuition that taste is a spectrum, not an exact value.
- **Easy to experiment with.** Because scoring is just weighted features, changing a single weight visibly reshapes the results — which made the energy-vs-genre experiment easy to run and reason about.

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

- **Grow and balance the catalog.** More songs across more genres would reduce the filter-bubble problem where a rock or jazz fan only ever sees one or two tracks.
- **Soften categorical matching.** Give partial credit for related genres and moods (e.g. "pop" ↔ "indie pop", "chill" ↔ "relaxed") instead of exact-match-only, so near-misses aren't unfairly zeroed out.
- **Add a diversity/novelty step.** Penalize near-duplicate results so the top 5 isn't two nearly-identical songs, and mix in some variety rather than the single closest cluster.
- **Learn preferences instead of asking for them.** Infer taste from listening history rather than requiring the user to type in numeric targets they can't realistically estimate.
- **Richer features and better explanations.** Consider lyrics, language, artist, and era, and turn the score breakdown into friendlier natural-language reasons.

---

## 9. Personal Reflection  

**Biggest learning moment.** The clearest lesson was how much the *weights* — not the features themselves — decide the outcome. Watching a single change (doubling energy, halving genre) pull cross-genre songs into a listener's top 5 made "algorithmic bias" feel concrete: no one intended a rock fan to see pop tracks, it just fell out of the numbers.

**How AI coding assistants helped.** The assistant was fastest at the mechanical, well-defined parts — wiring up CSV loading, structuring the weighted-scoring loop, generating the per-feature explanations, and setting up the three test profiles. It also helped me run a clean before/after comparison for the weight experiment and organize the model card.

**Where AI suggestions needed verification.** I couldn't take the scoring on trust — I had to actually run the profiles and check that scores matched the explanations, that weights summed to 1 after renormalization, and that the "close enough" numeric similarity behaved correctly (especially tempo, which lives on a different scale than the 0–1 features). The suggestions were plausible-looking but had to be validated against real output before I believed them.

**What surprised me about simple recommendation algorithms.** How convincing a very simple rule can look. With only weighted feature-matching and no machine learning at all, the top picks felt genuinely "right" — which is exactly what makes the hidden biases dangerous: a confident, sensible-looking list can still be quietly funneling people toward the same few songs.

**Future improvements.** I'd most want to add related-genre/mood matching and a diversity step, since those two changes would directly address the filter-bubble and near-duplicate problems I saw during evaluation.
