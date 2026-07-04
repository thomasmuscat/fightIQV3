from __future__ import annotations
import pandas as pd
from bs4 import BeautifulSoup

from fightiq.config import MAX_EVENTS, MAX_FIGHTS
from fightiq.scraper.http import soup_from_url
from fightiq.utils.text import clean_text, parse_fraction, slugify, stable_uuid, time_to_seconds, to_int

def stacked(col) -> list[str | None]:
    ps = col.select("p")
    if ps:
        return [clean_text(p.get_text(" ", strip=True)) for p in ps]
    return [clean_text(col.get_text(" ", strip=True))]

def parse_event_fight_rows(event: dict, fighter_lookup: dict[str, str]):
    soup = soup_from_url(event["ufcstats_url"])
    rows = soup.select("tr.b-fight-details__table-row")
    fights = []
    fight_urls = []

    for index, row in enumerate(rows):
        cols = row.select("td")
        if len(cols) < 10:
            continue

        fighter_links = cols[1].select("a")
        names = [clean_text(a.get_text(" ", strip=True)) for a in fighter_links]
        names = [n for n in names if n]
        if len(names) < 2:
            continue

        red_name, blue_name = names[0], names[1]
        red_slug, blue_slug = slugify(red_name), slugify(blue_name)
        red_id = fighter_lookup.get(red_slug, stable_uuid("fighter", red_slug))
        blue_id = fighter_lookup.get(blue_slug, stable_uuid("fighter", blue_slug))

        result_text = clean_text(cols[0].get_text(" ", strip=True))
        winner_id = red_id if result_text and "win" in result_text.lower() else None

        weight_class = clean_text(cols[6].get_text(" ", strip=True)) if len(cols) > 6 else None
        method = clean_text(cols[7].get_text(" ", strip=True)) if len(cols) > 7 else None
        round_num = to_int(cols[8].get_text(" ", strip=True)) if len(cols) > 8 else None
        time_text = clean_text(cols[9].get_text(" ", strip=True)) if len(cols) > 9 else None

        fight_url = row.get("data-link")
        fight_slug = slugify(f"{event['slug']}-{red_slug}-vs-{blue_slug}")
        fight_id = stable_uuid("fight", fight_slug)

        fights.append({
            "id": fight_id,
            "event_id": event["id"],
            "fighter_red_id": red_id,
            "fighter_blue_id": blue_id,
            "winner_id": winner_id,
            "weight_class": weight_class,
            "method": method,
            "round": round_num,
            "time": time_text,
            "is_title_fight": False,
            "is_main_event": index == 0,
            "ufcstats_url": fight_url,
            "data_source": "ufcstats_github_actions_ultra",
        })
        if fight_url:
            fight_urls.append((fight_url, fight_id, red_id, blue_id))

    return fights, fight_urls

def parse_fight_detail_stats(fight_url: str, fight_id: str, red_id: str, blue_id: str) -> list[dict]:
    soup = soup_from_url(fight_url)
    records = []

    # Totals table
    total_rows = soup.select("tbody.b-fight-details__table-body tr.b-fight-details__table-row")
    if not total_rows:
        return records

    row = total_rows[0]
    cols = row.select("td")
    if len(cols) < 10:
        return records

    # UFCStats total columns commonly:
    # 0 fighter, 1 KD, 2 Sig str, 3 Sig %, 4 Total str, 5 TD, 6 TD %, 7 Sub, 8 Rev, 9 Ctrl
    kd = stacked(cols[1]) if len(cols) > 1 else []
    sig = stacked(cols[2]) if len(cols) > 2 else []
    total = stacked(cols[4]) if len(cols) > 4 else []
    td = stacked(cols[5]) if len(cols) > 5 else []
    sub = stacked(cols[7]) if len(cols) > 7 else []
    rev = stacked(cols[8]) if len(cols) > 8 else []
    ctrl = stacked(cols[9]) if len(cols) > 9 else []

    # Significant strikes detail table
    sig_rows = soup.select("tbody.b-fight-details__table-body_js tr.b-fight-details__table-row")
    sig_detail = {}
    if sig_rows:
        srow = sig_rows[0]
        scols = srow.select("td")
        # Common: 0 fighter, 1 sig, 2 sig%, 3 head, 4 body, 5 leg, 6 distance, 7 clinch, 8 ground
        for key, idx in [
            ("head", 3),
            ("body", 4),
            ("leg", 5),
            ("distance", 6),
            ("clinch", 7),
            ("ground", 8),
        ]:
            if len(scols) > idx:
                sig_detail[key] = stacked(scols[idx])

    for idx, fighter_id in enumerate([red_id, blue_id]):
        sig_l, sig_a = parse_fraction(sig[idx] if idx < len(sig) else None)
        total_l, total_a = parse_fraction(total[idx] if idx < len(total) else None)
        td_l, td_a = parse_fraction(td[idx] if idx < len(td) else None)
        head_l, _ = parse_fraction(sig_detail.get("head", [None, None])[idx] if idx < len(sig_detail.get("head", [])) else None)
        body_l, _ = parse_fraction(sig_detail.get("body", [None, None])[idx] if idx < len(sig_detail.get("body", [])) else None)
        leg_l, _ = parse_fraction(sig_detail.get("leg", [None, None])[idx] if idx < len(sig_detail.get("leg", [])) else None)
        distance_l, _ = parse_fraction(sig_detail.get("distance", [None, None])[idx] if idx < len(sig_detail.get("distance", [])) else None)
        clinch_l, _ = parse_fraction(sig_detail.get("clinch", [None, None])[idx] if idx < len(sig_detail.get("clinch", [])) else None)
        ground_l, _ = parse_fraction(sig_detail.get("ground", [None, None])[idx] if idx < len(sig_detail.get("ground", [])) else None)

        records.append({
            "id": stable_uuid("fight_stat", f"{fight_id}-{fighter_id}"),
            "fight_id": fight_id,
            "fighter_id": fighter_id,
            "knockdowns": to_int(kd[idx], default=0) if idx < len(kd) else None,
            "sig_strikes_landed": sig_l,
            "sig_strikes_attempted": sig_a,
            "total_strikes_landed": total_l,
            "total_strikes_attempted": total_a,
            "takedowns_landed": td_l,
            "takedowns_attempted": td_a,
            "submission_attempts": to_int(sub[idx], default=0) if idx < len(sub) else None,
            "reversals": to_int(rev[idx], default=0) if idx < len(rev) else None,
            "control_time_seconds": time_to_seconds(ctrl[idx]) if idx < len(ctrl) else None,
            "head_landed": head_l,
            "body_landed": body_l,
            "leg_landed": leg_l,
            "distance_landed": distance_l,
            "clinch_landed": clinch_l,
            "ground_landed": ground_l,
            "data_source": "ufcstats_github_actions_ultra",
        })

    return records

def scrape_fights(events_df: pd.DataFrame, fighters_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    fighter_lookup = {row.slug: row.id for row in fighters_df.itertuples()} if not fighters_df.empty else {}
    events = events_df.to_dict("records")
    if MAX_EVENTS:
        events = events[:int(MAX_EVENTS)]

    all_fights = []
    all_stats = []
    fight_urls = []

    for i, event in enumerate(events, start=1):
        print(f"[fights] event {i}/{len(events)} {event.get('name')}")
        try:
            fights, urls = parse_event_fight_rows(event, fighter_lookup)
            all_fights.extend(fights)
            fight_urls.extend(urls)
            print(f"[fights] rows={len(fights)}")
        except Exception as exc:
            print(f"[fights] event failed {event.get('name')}: {exc}")

    if MAX_FIGHTS:
        fight_urls = fight_urls[:int(MAX_FIGHTS)]

    for i, (url, fight_id, red_id, blue_id) in enumerate(fight_urls, start=1):
        print(f"[fight_stats] {i}/{len(fight_urls)} {url}")
        try:
            all_stats.extend(parse_fight_detail_stats(url, fight_id, red_id, blue_id))
        except Exception as exc:
            print(f"[fight_stats] failed {url}: {exc}")

    fights_df = pd.DataFrame(all_fights)
    stats_df = pd.DataFrame(all_stats)

    if not fights_df.empty:
        fights_df = fights_df.drop_duplicates("id").reset_index(drop=True)
    if not stats_df.empty:
        stats_df = stats_df.drop_duplicates("id").reset_index(drop=True)

    return fights_df, stats_df
