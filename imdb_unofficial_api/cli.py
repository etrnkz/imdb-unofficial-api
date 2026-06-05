import argparse
import sys
from imdb_unofficial_api import ImdbClient


def print_title(t, indent=""):
    print(f"{indent}ID: {t.id}")
    print(f"{indent}Title: {t.title}")
    if t.release_year:
        print(f"{indent}Year: {t.release_year}")
    if t.title_type:
        print(f"{indent}Type: {t.title_type}")
    if t.rating:
        print(f"{indent}Rating: {t.rating.aggregate_rating} ({t.rating.vote_count} votes)")
        if t.rating.top_rank:
            print(f"{indent}Rank: #{t.rating.top_rank}")
    if t.plot_outline:
        print(f"{indent}Plot: {t.plot_outline[:200]}...")
    if t.runtime_minutes:
        print(f"{indent}Runtime: {t.runtime_minutes} min")
    if t.genres:
        print(f"{indent}Genres: {', '.join(t.genres)}")
    if t.directors:
        print(f"{indent}Director: {t.directors[0].name}")
    if t.writers:
        print(f"{indent}Writers: {', '.join(w.name for w in t.writers[:3])}")
    if t.taglines:
        print(f"{indent}Tagline: {t.taglines[0]}")
    if t.recommendations:
        print(f"{indent}Recommendations:")
        for rec in t.recommendations[:5]:
            r = rec.rating.aggregate_rating if rec.rating else "N/A"
            print(f"{indent}  - {rec.title} ({rec.release_year}) - {r}")
    if t.episode_info:
        ei = t.episode_info
        print(f"{indent}Episode: S{ei.season_number}E{ei.episode_number}")


def cmd_get(args):
    with ImdbClient() as client:
        t = client.get_title(args.id)
        if t:
            print_title(t)
        else:
            print("Title not found")


def cmd_search(args):
    with ImdbClient() as client:
        results = client.search(args.query, first=args.first)
        for r in results:
            print(f"{r.id}  {r.title} ({r.year or 'N/A'})  [{r.title_type}]  {r.rating or 'N/A'}")


def cmd_person(args):
    with ImdbClient() as client:
        n = client.get_name(args.id)
        if n:
            print(f"ID: {n.id}")
            print(f"Name: {n.name}")
            if n.birth_date:
                print(f"Born: {n.birth_date}")
            if n.death_date:
                print(f"Died: {n.death_date}")
            if n.bio:
                print(f"Bio: {n.bio[:300]}...")
            print(f"Filmography ({len(n.filmography)} titles):")
            for f in n.filmography[:10]:
                r = f.rating.aggregate_rating if f.rating else "N/A"
                print(f"  - {f.title} ({f.release_year or 'N/A'}) [{f.title_type}] {r}")
        else:
            print("Person not found")


def cmd_cast(args):
    with ImdbClient() as client:
        cast = client.get_title_cast(args.id)
        print(f"Cast ({len(cast)}):")
        for c in cast[:20]:
            chars = ", ".join(c.characters) if c.characters else ""
            print(f"  {c.name}  [{chars}]")


def cmd_seasons(args):
    with ImdbClient() as client:
        seasons = client.get_title_seasons(args.id)
        print(f"Seasons ({len(seasons)}):")
        for s in seasons:
            print(f"  Season {s.season_number}")


def cmd_episodes(args):
    with ImdbClient() as client:
        eps = client.get_title_episodes(args.id, season=args.season, first=args.first)
        print(f"Episodes ({len(eps)}):")
        for e in eps:
            ei = e.episode_info
            s = f"  S{ei.season_number}E{ei.episode_number} - {e.title} ({e.release_year})"
            if e.rating:
                s += f" - {e.rating.aggregate_rating}"
            print(s)


def cmd_reviews(args):
    with ImdbClient() as client:
        user_reviews, mc_reviews, mc_score = client.get_title_reviews(args.id)
        if mc_score is not None:
            print(f"Metacritic Score: {mc_score}")
        if mc_reviews:
            print(f"Critic Reviews ({len(mc_reviews)}):")
            for r in mc_reviews[:5]:
                print(f"  {r.score:>3}  {r.site or 'N/A'}  {r.reviewer or 'N/A'} | {r.quote or ''}")
        if user_reviews:
            print(f"\nUser Reviews ({len(user_reviews)}):")
            for r in user_reviews[:5]:
                print(f"  [{r.author_rating}/10] {r.author}")
                if r.summary:
                    print(f"  {r.summary[:120]}")
                print()


def cmd_chart(args):
    chart_type = args.chart_type.upper().replace("-", "_").replace(" ", "_")
    with ImdbClient() as client:
        titles = client.get_chart(chart_type, first=args.first)
        for i, t in enumerate(titles, 1):
            r = t.rating.aggregate_rating if t.rating else "N/A"
            print(f"#{i:>3}  {r:>3}  {t.title} ({t.release_year or 'N/A'})")


def cmd_trending(args):
    with ImdbClient() as client:
        titles = client.get_trending(limit=args.first)
        for t in titles:
            r = t.rating.aggregate_rating if t.rating else "N/A"
            print(f"  {r:>3}  {t.title} ({t.release_year or 'N/A'})")


def cmd_popular(args):
    with ImdbClient() as client:
        titles = client.get_popular(limit=args.first)
        for t in titles:
            r = t.rating.aggregate_rating if t.rating else "N/A"
            print(f"  {r:>3}  {t.title} ({t.release_year or 'N/A'})")


def main():
    parser = argparse.ArgumentParser(prog="imdb", description="IMDb Unofficial API CLI")
    parser.add_argument("--version", action="version", version="imdb-unofficial-api 1.0.0")

    sub = parser.add_subparsers(dest="command")

    p_get = sub.add_parser("get", help="Get title details")
    p_get.add_argument("id", help="IMDb ID (e.g. tt1375666)")

    p_search = sub.add_parser("search", help="Search titles")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("-n", "--first", type=int, default=20, help="Number of results")

    p_person = sub.add_parser("person", help="Get person/actor details")
    p_person.add_argument("id", help="IMDb ID (e.g. nm0000151)")

    p_cast = sub.add_parser("cast", help="Get title cast")
    p_cast.add_argument("id", help="IMDb ID (e.g. tt1375666)")

    p_seasons = sub.add_parser("seasons", help="List seasons")
    p_seasons.add_argument("id", help="IMDb ID (e.g. tt0903747)")

    p_eps = sub.add_parser("episodes", help="List episodes")
    p_eps.add_argument("id", help="IMDb ID")
    p_eps.add_argument("-s", "--season", help="Season number")
    p_eps.add_argument("-n", "--first", type=int, default=50, help="Number of episodes")

    p_reviews = sub.add_parser("reviews", help="Get reviews")
    p_reviews.add_argument("id", help="IMDb ID")

    p_chart = sub.add_parser("chart", help="Get chart")
    chart_help = "Chart type: top_rated_movies, top_rated_tv_shows, most_popular_movies, most_popular_tv_shows"
    p_chart.add_argument("chart_type", help=chart_help)
    p_chart.add_argument("-n", "--first", type=int, default=50, help="Number of titles")

    p_trending = sub.add_parser("trending", help="Get trending titles")
    p_trending.add_argument("-n", "--first", type=int, default=20, help="Number of titles")

    p_popular = sub.add_parser("popular", help="Get popular titles")
    p_popular.add_argument("-n", "--first", type=int, default=20, help="Number of titles")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "get": cmd_get,
        "search": cmd_search,
        "person": cmd_person,
        "cast": cmd_cast,
        "seasons": cmd_seasons,
        "episodes": cmd_episodes,
        "reviews": cmd_reviews,
        "chart": cmd_chart,
        "trending": cmd_trending,
        "popular": cmd_popular,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
