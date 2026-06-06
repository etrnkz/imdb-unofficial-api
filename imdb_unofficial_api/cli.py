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


def cmd_trailer(args):
    with ImdbClient() as client:
        t = client.get_title_trailer(args.id)
        if t:
            print(f"Name: {t.name}")
            print(f"Type: {t.content_type}")
            print(f"Duration: {t.duration_seconds}s")
            print(f"Thumbnail: {t.thumbnail_url}")
            print("Playback URLs:")
            for fmt, url in t.playback_urls.items():
                print(f"  {fmt}: {url}")
        else:
            print("No trailer found")


def cmd_trivia(args):
    with ImdbClient() as client:
        items = client.get_title_trivia(args.id)
        print(f"Trivia ({len(items)}):")
        for i, item in enumerate(items, 1):
            print(f"\n#{i}: {item.text}")


def cmd_quotes(args):
    with ImdbClient() as client:
        items = client.get_title_quotes(args.id)
        print(f"Quotes ({len(items)}):")
        for i, item in enumerate(items, 1):
            print(f"\n#{i}: {item.text}")


def cmd_goofs(args):
    with ImdbClient() as client:
        items = client.get_title_goofs(args.id)
        print(f"Goofs ({len(items)}):")
        for i, item in enumerate(items, 1):
            print(f"\n#{i} [{item.category}]: {item.text}")


def cmd_locations(args):
    with ImdbClient() as client:
        items = client.get_title_filming_locations(args.id)
        print(f"Filming Locations ({len(items)}):")
        for i, loc in enumerate(items, 1):
            attrs = ", ".join(loc["attributes"])
            attr_str = f" [{attrs}]" if attrs else ""
            print(f"\n#{i}: {loc['location']}{attr_str}")
            if loc["text"]:
                print(f"   {loc['text']}")


def cmd_box_office(args):
    with ImdbClient() as client:
        bo = client.get_title_box_office(args.id)
        print(f"Budget: ${bo.budget:,} {bo.budget_currency}" if bo.budget else "Budget: N/A")
        print(f"Lifetime Gross: ${bo.lifetime_gross:,} {bo.lifetime_currency}" if bo.lifetime_gross else "Lifetime Gross: N/A")
        if bo.opening_weekend_gross:
            print(f"Opening Weekend: ${bo.opening_weekend_gross:,} {bo.opening_weekend_currency} ({bo.opening_theaters} theaters)")
        else:
            print("Opening Weekend: N/A")


def cmd_company_credits(args):
    with ImdbClient() as client:
        items = client.get_title_company_credits(args.id)
        print(f"Company Credits ({len(items)}):")
        for i, c in enumerate(items, 1):
            print(f"  #{i} [{c.category}] {c.company_name} ({c.company_id})")


def cmd_tech_specs(args):
    with ImdbClient() as client:
        ts = client.get_title_tech_specs(args.id)
        if ts.aspect_ratios:
            print(f"Aspect Ratios: {', '.join(ts.aspect_ratios)}")
        if ts.sound_mixes:
            print(f"Sound Mixes: {', '.join(ts.sound_mixes)}")
        if ts.colorations:
            print(f"Colorations: {', '.join(ts.colorations)}")
        if ts.cameras:
            print(f"Cameras: {', '.join(ts.cameras)}")


def cmd_release_dates(args):
    with ImdbClient() as client:
        items = client.get_title_release_dates(args.id)
        print(f"Release Dates ({len(items)}):")
        for i, rd in enumerate(items, 1):
            date = f"{rd.year}-{rd.month:02d}-{rd.day:02d}" if rd.year and rd.month and rd.day else f"{rd.year or 'N/A'}"
            attrs = ", ".join(rd.attributes) if rd.attributes else ""
            attr_str = f" [{attrs}]" if attrs else ""
            print(f"  #{i} {rd.country or 'N/A'}: {date}{attr_str}")


def cmd_parents_guide(args):
    with ImdbClient() as client:
        items = client.get_title_parents_guide(args.id)
        print(f"Parents Guide ({len(items)}):")
        for i, pg in enumerate(items, 1):
            print(f"\n  #{i} [{pg.category}]:")
            if pg.text:
                print(f"    {pg.text[:200]}")


def cmd_keywords(args):
    with ImdbClient() as client:
        items = client.get_title_keywords(args.id)
        print(f"Keywords ({len(items)}):")
        for i, kw in enumerate(items, 1):
            print(f"  #{i} {kw.text} ({kw.legacy_id})")


def cmd_awards(args):
    with ImdbClient() as client:
        items = client.get_title_awards(args.id)
        print(f"Awards & Nominations ({len(items)}):")
        for i, a in enumerate(items, 1):
            winner = "WON" if a.is_winner else "NOMINATED"
            print(f"  #{i} [{winner}] {a.award_name} - {a.category}")
            if a.notes:
                print(f"       {a.notes[:150]}")


def cmd_watch(args):
    with ImdbClient() as client:
        wo = client.get_title_watch_options(args.id)
        if wo:
            print(f"Provider: {wo.provider}")
            print(f"Offer: {wo.offer_type}")
            print(f"Link: {wo.link}")
            print(f"Description: {wo.description}")
        else:
            print("No watch options found")


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

    p_trailer = sub.add_parser("trailer", help="Get title trailer")
    p_trailer.add_argument("id", help="IMDb ID")

    p_trivia = sub.add_parser("trivia", help="Get title trivia")
    p_trivia.add_argument("id", help="IMDb ID")

    p_quotes = sub.add_parser("quotes", help="Get title quotes")
    p_quotes.add_argument("id", help="IMDb ID")

    p_goofs = sub.add_parser("goofs", help="Get title goofs")
    p_goofs.add_argument("id", help="IMDb ID")

    p_locs = sub.add_parser("locations", help="Get filming locations")
    p_locs.add_argument("id", help="IMDb ID")

    p_box = sub.add_parser("box-office", help="Get box office data")
    p_box.add_argument("id", help="IMDb ID")

    p_cc = sub.add_parser("company-credits", help="Get company credits")
    p_cc.add_argument("id", help="IMDb ID")

    p_ts = sub.add_parser("tech-specs", help="Get technical specifications")
    p_ts.add_argument("id", help="IMDb ID")

    p_rd = sub.add_parser("release-dates", help="Get release dates")
    p_rd.add_argument("id", help="IMDb ID")

    p_pg = sub.add_parser("parents-guide", help="Get parents guide")
    p_pg.add_argument("id", help="IMDb ID")

    p_kw = sub.add_parser("keywords", help="Get keywords")
    p_kw.add_argument("id", help="IMDb ID")

    p_aw = sub.add_parser("awards", help="Get awards and nominations")
    p_aw.add_argument("id", help="IMDb ID")

    p_wo = sub.add_parser("watch", help="Get watch options")
    p_wo.add_argument("id", help="IMDb ID")

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
        "trailer": cmd_trailer,
        "trivia": cmd_trivia,
        "quotes": cmd_quotes,
        "goofs": cmd_goofs,
        "locations": cmd_locations,
        "box-office": cmd_box_office,
        "company-credits": cmd_company_credits,
        "tech-specs": cmd_tech_specs,
        "release-dates": cmd_release_dates,
        "parents-guide": cmd_parents_guide,
        "keywords": cmd_keywords,
        "awards": cmd_awards,
        "watch": cmd_watch,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
