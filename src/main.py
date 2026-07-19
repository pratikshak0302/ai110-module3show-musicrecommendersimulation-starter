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


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 60
    print()
    print("=" * width)
    print(f"  TOP {len(recommendations)} RECOMMENDATIONS".ljust(width))
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


if __name__ == "__main__":
    main()
