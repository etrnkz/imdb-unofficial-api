import sys, time

sys.stdout.reconfigure(encoding="utf-8")
from imdb_unofficial_api import ImdbClient

T = "tt1375666"  # Inception
N = "nm0000138"  # Leonardo DiCaprio
TV = "tt0944947"  # Game of Thrones

results = {"pass": 0, "fail": 0, "errors": []}


def test(name, fn):
    try:
        r = fn()
        if r is not None:
            results["pass"] += 1
        else:
            results["fail"] += 1
            results["errors"].append(f"{name}: returned None")
    except Exception as e:
        results["fail"] += 1
        results["errors"].append(f"{name}: {e}")
    print(f"  {'OK' if results['pass'] > 0 and 'fail' not in name else '  '} {name}")


print("=== TITLES ===")
with ImdbClient() as c:
    test("get_title", lambda: c.get_title(T))
    test("get_titles", lambda: c.get_titles(T, "tt0816692"))
    test("search", lambda: c.search("Inception", first=3))
    test("search_page", lambda: c.search_page("Inception", first=3))
    test("search_advanced", lambda: c.search_advanced(query="Inception", first=3))
    test(
        "search_advanced_page",
        lambda: c.search_advanced_page(query="Inception", first=3),
    )
    test("get_title_cast", lambda: c.get_title_cast(T))
    test("get_title_cast_category", lambda: c.get_title_cast(T, category="CAST"))
    test("get_title_seasons", lambda: c.get_title_seasons(TV))
    test("get_title_episodes", lambda: c.get_title_episodes(TV, season="1"))
    test("get_title_reviews", lambda: c.get_title_reviews(T))
    test("get_title_trailer", lambda: c.get_title_trailer(T))

    print("\n=== TITLE CONTENT ===")
    test("get_title_trivia", lambda: c.get_title_trivia(T))
    test("get_title_quotes", lambda: c.get_title_quotes(T))
    test("get_title_goofs", lambda: c.get_title_goofs(T))
    test("get_title_filming_locations", lambda: c.get_title_filming_locations(T))
    test("get_title_plots", lambda: c.get_title_plots(T))
    test("get_title_images", lambda: c.get_title_images(T))
    test("get_title_soundtrack", lambda: c.get_title_soundtrack(T))
    test("get_title_videos", lambda: c.get_title_videos(T))

    print("\n=== TITLE BUSINESS ===")
    test("get_title_box_office", lambda: c.get_title_box_office(T))
    test("get_title_company_credits", lambda: c.get_title_company_credits(T))
    test("get_title_tech_specs", lambda: c.get_title_tech_specs(T))
    test("get_title_release_dates", lambda: c.get_title_release_dates(T))
    test("get_title_parents_guide", lambda: c.get_title_parents_guide(T))
    test("get_title_keywords", lambda: c.get_title_keywords(T))
    test("get_title_awards", lambda: c.get_title_awards(T))
    test("get_title_watch_options", lambda: c.get_title_watch_options(T))
    test("get_title_certificate", lambda: c.get_title_certificate(T))
    test("get_title_production_status", lambda: c.get_title_production_status(T))
    test("get_title_engagement_stats", lambda: c.get_title_engagement_stats(T))
    test("get_title_rating_histogram", lambda: c.get_title_rating_histogram(T))
    test("get_title_meta", lambda: c.get_title_meta(T))

    print("\n=== CONNECTIONS & EXTERNAL ===")
    test("get_title_connections", lambda: c.get_title_connections(T))
    test("get_title_akas", lambda: c.get_title_akas(T))
    test("get_title_external_links", lambda: c.get_title_external_links(T))
    test("get_title_crazy_credits", lambda: c.get_title_crazy_credits(T))
    test("get_title_faqs", lambda: c.get_title_faqs(T))
    test("get_title_news", lambda: c.get_title_news(T))
    test("get_title_recommendations", lambda: c.get_title_recommendations(T))
    test("get_title_interests", lambda: c.get_title_interests(T))
    test("get_title_related_lists", lambda: c.get_title_related_lists(T))

    print("\n=== CHARTS ===")
    test("get_chart", lambda: c.get_chart("TOP_RATED_MOVIES", first=3))
    test("get_top_rated_movies", lambda: c.get_top_rated_movies(3))
    test("get_top_rated_tv", lambda: c.get_top_rated_tv(3))
    test("get_most_popular_movies", lambda: c.get_most_popular_movies(3))
    test("get_most_popular_tv", lambda: c.get_most_popular_tv(3))
    test("get_lowest_rated_movies", lambda: c.get_lowest_rated_movies(3))
    test("get_trending", lambda: c.get_trending(3))
    test("get_popular", lambda: c.get_popular(3))

    print("\n=== NAMES ===")
    test("get_name", lambda: c.get_name(N))
    test("get_names", lambda: c.get_names(N, "nm0000158"))
    test("search_person", lambda: c.search_person("DiCaprio", first=3))
    test("search_person_page", lambda: c.search_person_page("DiCaprio", first=3))
    test("get_name_known_for", lambda: c.get_name_known_for(N, first=3))
    test(
        "get_name_filmography_titles", lambda: c.get_name_filmography_titles(N, first=3)
    )
    test("get_name_height", lambda: c.get_name_height(N))
    test("get_name_age", lambda: c.get_name_age(N))
    test("get_name_birth_details", lambda: c.get_name_birth_details(N))
    test("get_name_death_details", lambda: c.get_name_death_details(N))
    test("get_name_spouses", lambda: c.get_name_spouses(N))
    test("get_name_awards", lambda: c.get_name_awards(N))
    test("get_name_images", lambda: c.get_name_images(N))
    test("get_name_credits", lambda: c.get_name_credits(N))
    test("get_name_other_works", lambda: c.get_name_other_works(N))
    test("get_name_trivia", lambda: c.get_name_trivia(N))
    test("get_name_quotes", lambda: c.get_name_quotes(N))
    test("get_name_trademarks", lambda: c.get_name_trademarks(N))

print(f"\n{'=' * 40}")
print(f"PASS: {results['pass']}  FAIL: {results['fail']}")
if results["errors"]:
    print(f"\nERRORS:")
    for e in results["errors"]:
        print(f"  - {e}")
