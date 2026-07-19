import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

# ---------------------------------------------------------------------------
# Scoring helpers (shared by the functional and OOP paths)
# ---------------------------------------------------------------------------

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def _match(a: Optional[str], b: Optional[str]) -> bool:
    """Case-insensitive string match, tolerant of None."""
    if a is None or b is None:
        return False
    return str(a).strip().lower() == str(b).strip().lower()

def _closeness(target: float, value: float) -> float:
    """Similarity in [0, 1] for two values on a 0..1 scale (1 = identical)."""
    return _clamp01(1.0 - abs(float(target) - float(value)))

def _tempo_closeness(target: float, value: float, scale: float = 60.0) -> float:
    """Similarity in [0, 1] for tempo, where a `scale` BPM gap → 0."""
    return _clamp01(1.0 - abs(float(target) - float(value)) / scale)


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score a Song against a UserProfile. Returns (score, reasons)."""
        weights = {"genre": 0.35, "mood": 0.25, "energy": 0.25, "acoustic": 0.15}
        reasons: List[str] = []
        total = 0.0

        if _match(user.favorite_genre, song.genre):
            total += weights["genre"]
            reasons.append(f"matches your favorite genre ({song.genre})")
        if _match(user.favorite_mood, song.mood):
            total += weights["mood"]
            reasons.append(f"matches your {song.mood} mood")

        energy_sim = _closeness(user.target_energy, song.energy)
        total += weights["energy"] * energy_sim
        if energy_sim >= 0.8:
            reasons.append(f"energy ({song.energy}) is close to your target ({user.target_energy})")

        # likes_acoustic True -> reward high acousticness, False -> reward low
        acoustic_sim = song.acousticness if user.likes_acoustic else (1.0 - song.acousticness)
        total += weights["acoustic"] * acoustic_sim
        if acoustic_sim >= 0.7:
            reasons.append("acousticness fits your preference")

        return total, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        ranked = sorted(self.songs, key=lambda s: self._score(user, s)[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = self._score(user, song)
        if reasons:
            return f"Recommended (score {score:.2f}) because it " + "; ".join(reasons) + "."
        return f"Recommended (score {score:.2f}) as a partial match on your preferences."


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dicts, casting numeric columns.
    Required by src/main.py
    """
    int_fields = {"id", "tempo_bpm"}
    float_fields = {"energy", "valence", "danceability", "acousticness"}
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            song: Dict = {}
            for key, value in row.items():
                if key in int_fields:
                    song[key] = int(value)
                elif key in float_fields:
                    song[key] = float(value)
                else:
                    song[key] = value
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song (dict) against user preferences (dict).

    Algorithm Recipe:
      - genre match      -> +0.25
      - mood match       -> +0.20
      - energy           -> similarity * 0.15
      - tempo_bpm        -> similarity * 0.10
      - danceability     -> similarity * 0.15
      - valence          -> similarity * 0.15

    Numeric similarity = 1 - abs(song_value - user_value), clamped to [0, 1].
    tempo_bpm is on a 60-180 scale, so its gap is divided by 60 BPM before the
    formula (otherwise a 2-BPM difference would score negative).

    Accepts either `target_*` keys (favorite_genre, target_energy, ...) or the
    simple keys (genre, mood, energy). Only the preferences present are scored,
    and the score is normalized to [0, 1] over the weights actually used.
    Returns (score, reasons), e.g. "genre match (+0.25)",
    "energy similarity (0.93 x 0.15)".
    """
    # Pull preferences, supporting both key styles.
    genre_pref = user_prefs.get("favorite_genre", user_prefs.get("genre"))
    mood_pref = user_prefs.get("favorite_mood", user_prefs.get("mood"))
    energy_pref = user_prefs.get("target_energy", user_prefs.get("energy"))
    tempo_pref = user_prefs.get("target_tempo_bpm", user_prefs.get("tempo_bpm"))
    dance_pref = user_prefs.get("target_danceability", user_prefs.get("danceability"))
    valence_pref = user_prefs.get("target_valence", user_prefs.get("valence"))

    # Scoring experiment: double energy's weight (0.15 -> 0.30) and halve
    # genre's (0.25 -> 0.125). These raw values sum to 1.025, so we renormalize
    # by their total to keep the weight set summing to exactly 1.0.
    raw_weights = {
        "genre": 0.125, "mood": 0.20, "energy": 0.30,
        "tempo": 0.10, "danceability": 0.15, "valence": 0.15,
    }
    total_weight = sum(raw_weights.values())  # 1.025
    weights = {name: w / total_weight for name, w in raw_weights.items()}

    reasons: List[str] = []
    weighted_sum = 0.0
    used_weight = 0.0

    # --- Categorical features: full points on an exact match ---
    if genre_pref is not None:
        used_weight += weights["genre"]
        if _match(genre_pref, song.get("genre")):
            weighted_sum += weights["genre"]
            reasons.append(f"genre match (+{weights['genre']:.2f})")

    if mood_pref is not None:
        used_weight += weights["mood"]
        if _match(mood_pref, song.get("mood")):
            weighted_sum += weights["mood"]
            reasons.append(f"mood match (+{weights['mood']:.2f})")

    # --- Numerical features: reward closeness to the target ---
    numeric = [
        ("energy", energy_pref, _closeness, "energy"),
        ("tempo", tempo_pref, _tempo_closeness, "tempo_bpm"),
        ("danceability", dance_pref, _closeness, "danceability"),
        ("valence", valence_pref, _closeness, "valence"),
    ]
    for name, pref, sim_fn, field in numeric:
        if pref is None or song.get(field) is None:
            continue
        weight = weights[name]
        used_weight += weight
        sim = sim_fn(pref, song[field])
        weighted_sum += weight * sim
        reasons.append(f"{name} similarity ({sim:.2f} x {weight:.2f})")

    score = weighted_sum / used_weight if used_weight else 0.0
    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song, ranks best-first, and returns the top k.
    Each item is (song_dict, score, explanation).
    Required by src/main.py
    """
    def evaluate(song: Dict) -> Tuple[Dict, float, str]:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "partial match on your preferences"
        return song, score, explanation

    scored = [evaluate(song) for song in songs]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranked[:k]
