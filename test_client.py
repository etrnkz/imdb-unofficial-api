from imdb_unofficial_api import ImdbClient
import json

client = ImdbClient()

print("=" * 60)
print("TEST 1: Get Title (The Shawshank Redemption - tt0111161)")
print("=" * 60)
title = client.get_title("tt0111161")
if title:
    print(f"ID: {title.id}")
    print(f"Title: {title.title}")
    print(f"Original: {title.original_title}")
    print(f"Type: {title.title_type}")
    print(f"Year: {title.release_year}")
    print(f"Rating: {title.rating.aggregate_rating} ({title.rating.vote_count} votes)")
    if title.rating.top_rank:
        print(f"Top 250 Rank: #{title.rating.top_rank}")
    print(f"Plot: {title.plot_outline[:200] if title.plot_outline else 'N/A'}...")
    print(f"Runtime: {title.runtime_minutes} min")
    print(f"Genres: {title.genres}")
    print(f"Countries: {title.countries}")
    print(f"Languages: {title.languages}")
    print(f"Popularity Rank: {title.popularity_rank}")
    print(f"Directors: {[d.name for d in title.directors]}")
    print(f"Writers: {[w.name for w in title.writers]}")
    print(f"Taglines ({len(title.taglines)}): {title.taglines[:3]}")
    print(f"Recommendations ({len(title.recommendations)}):")
    for rec in title.recommendations[:5]:
        print(f"  - {rec.title} ({rec.release_year}) - {rec.rating.aggregate_rating if rec.rating else 'N/A'}")
else:
    print("Title not found!")

print()
print("=" * 60)
print("TEST 2: Search for Batman")
print("=" * 60)
results = client.search("Batman", first=10)
print(f"Found {len(results)} results:")
for r in results:
    print(f"  [{r.id}] {r.title} ({r.year}) - {r.title_type} - Rating: {r.rating}")

print()
print("=" * 60)
print("TEST 3: Get Person (Leonardo DiCaprio - nm0000138)")
print("=" * 60)
name = client.get_name("nm0000138")
if name:
    print(f"ID: {name.id}")
    print(f"Name: {name.name}")
    print(f"Birth: {name.birth_date}")
    print(f"Bio: {name.bio[:200] if name.bio else 'N/A'}...")
    print(f"Filmography ({len(name.filmography)} titles):")
    for f in name.filmography[:10]:
        print(f"  - {f.title} ({f.release_year}) [{f.title_type}]")
else:
    print("Name not found!")

print()
print("=" * 60)
print("TEST 4: Get Title Cast")
print("=" * 60)
cast = client.get_title_cast("tt0111161")
print(f"Total cast: {len(cast)}")
for c in cast[:10]:
    print(f"  {c.name} as {', '.join(c.characters) if c.characters else 'N/A'} ({c.person_id})")

client.close()
print("\nAll tests completed!")
