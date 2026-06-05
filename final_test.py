from imdb_unofficial_api import ImdbClient

client = ImdbClient()

tests = {
    "Movie (Inception)": "tt1375666",
    "TV Series (Breaking Bad)": "tt0903747",
    "TV Episode (Ozymandias)": "tt0959621",
    "Person (Morgan Freeman)": "nm0000151",
}

for label, tid in tests.items():
    print(f"=== {label} ===")
    if tid.startswith("nm"):
        n = client.get_name(tid)
        if n:
            print(f"  Name: {n.name}")
            print(f"  Known for: {len(n.filmography)} titles")
    else:
        t = client.get_title(tid)
        if t:
            print(f"  Title: {t.title}")
            print(f"  Type: {t.title_type}")
            r = t.rating.aggregate_rating if t.rating else "N/A"
            print(f"  Rating: {r}")
            print(f"  Genres: {t.genres[:3]}")
    print()

for q in ["Avatar", "The Matrix", "Game of Thrones"]:
    results = client.search(q, first=3)
    print(f'Search "{q}": {[r.title for r in results]}')

print()
print("=== Edge Cases ===")
cast = client.get_title_cast("tt1375666")
print(f"Cast of Inception: {len(cast)} cast members")
t = client.get_title("tt0903747")
print(f"Breaking Bad: {t.title}, Rating: {t.rating.aggregate_rating if t.rating else 'N/A'}, Episodes: {t.runtime_minutes}min")

client.close()
print("\nAll tests passed!")
