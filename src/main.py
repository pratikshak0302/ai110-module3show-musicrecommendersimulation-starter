"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    # Works when run as a package from the project root: `python -m src.main`
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    # Works when run directly from inside src/: `python main.py`
    from recommender import load_songs, recommend_songs


# Test profiles covering three very different listeners.
# Keys use the simple style (genre/mood/energy/...) supported by score_song.
# Values stay within the ranges and genres/moods present in data/songs.csv.
PROFILES = {
    "High-Energy Pop listener": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.90,
        "tempo_bpm": 130,
        "danceability": 0.85,
        "valence": 0.80,
    },
    "Chill Lofi listener": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "tempo_bpm": 75,
        "danceability": 0.60,
        "valence": 0.58,
    },
    "Deep Intense Rock listener": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.90,
        "tempo_bpm": 150,
        "danceability": 0.60,
        "valence": 0.45,
    },
}


def print_recommendations(name: str, recommendations, width: int = 60) -> None:
    print()
    print("=" * width)
    print(f"  {name}  (top {len(recommendations)})".ljust(width))
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print()
        print(f"{rank}. {song['title']}  -  {song['artist']}")
        print(f"   Score: {score:.2f} / 1.00")
        print("   Why recommended:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")

    print()
    print("=" * width)


def main() -> None:
    songs = load_songs("data/songs.csv")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, recommendations)


if __name__ == "__main__":
    main()
