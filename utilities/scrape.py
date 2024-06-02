from .helpers import fetch_url_content, parse_data, find_commented_tables, find_commented_divs, get_current_season_year, generate_nba_history
import re
import string
import time
import logging

# Fetch and parse active team data
def get_active_teams():
    stats_list = ['lg_id', 'year_min', 'year_max', 'years', 'g', 'wins', 'losses', 'win_loss_pct',
                  'years_playoffs', 'years_division_champion', 'years_conference_champion', 'years_league_champion']

    url = 'https://www.basketball-reference.com/teams/'
    soup = fetch_url_content(url)
    html_table = soup.find('table', {'id': 'teams_active'})

    active_teams_data = {}
    last_team_name = None  # Store the last "full_table" team name
    rows = html_table.find_all('tr')

    for row in rows:
        if 'full_table' in row.get('class', []):
            team_name = row.th.text.strip()
            active_teams_data[team_name] = {
                'Record': parse_data(row, stats_list), 'History': {}}
            last_team_name = team_name
        elif 'partial_table' in row.get('class', []):
            if last_team_name:
                active_teams_data[last_team_name]['History'][row.th.text.strip()] = parse_data(
                    row, stats_list)

    return active_teams_data

# Fetch and parse detailed team info
def get_team_info(team_id):
    current_year = get_current_season_year()
    current_url = f'https://www.basketball-reference.com/teams/{team_id}/{current_year}.html'
    meta_id = team_id  # Assuming no mapping needed
    meta_url = f'https://www.basketball-reference.com/teams/{meta_id}/'

    def parse_roster_table(table):
        rows = table.find_all('tr')[1:]
        players = []
        for row in rows:
            player_data = parse_data(row, ["player", "pos", "height", "weight", "birth_date", "college", "birth_country", "years_experience"])
            player_data["number"] = row.find('th', {'data-stat': 'number'}).text.strip()
            player_link = row.find('td', {'data-stat': 'player'}).find('a')
            player_data["id"] = player_link['href'].split('/')[-1].split('.')[0]
            if "player" in player_data:
                player_data["player"] = player_data["player"].replace("(TW)", "").strip()
            players.append(player_data)
        return players
    
    soup = fetch_url_content(current_url)
    html_table = soup.find('table', {'id': 'roster'})
    team_roster_data = parse_roster_table(html_table) if html_table else []

    html_record = soup.find('div', {'id': 'info'})
    meta_soup = fetch_url_content(meta_url)
    html_info = meta_soup.find('div', {'id': 'info'}).find('div', {'id': 'meta'})
    html_seasons_table = meta_soup.find('table', {'id': meta_id})

    def parse_seasons_table(table):
        rows = table.find_all('tr')[1:]
        seasons_dict = {}
        for row in rows:
            season_data = parse_data(row, ["season", "lg_id", "team_name", "wins", "losses",
                                           "win_loss_pct", "rank_team", "srs", "pace", "pace_rel",
                                           "off_rtg", "off_rtg_rel", "def_rtg", "def_rtg_rel",
                                           "rank_team_playoffs", "coaches", "top_ws"])
            seasons_dict[season_data["season"]] = season_data
        return seasons_dict

    def match_seasons_with_data(seasons_data, nba_history):
        new_history = []
        for decade in nba_history:
            for key, seasons in decade.items():
                filtered_seasons = [seasons_data.get(season, {}) for season in seasons if seasons_data.get(season, {})]
                if filtered_seasons:
                    new_history.append({key: filtered_seasons})
        return new_history

    nba_history = generate_nba_history()
    seasons_data = parse_seasons_table(html_seasons_table)
    new_nba_history = match_seasons_with_data(seasons_data, nba_history)

    team_stats = {
        "name": html_info.find_all('div')[1].find('h1').find_all('span')[0].text,
        "logo": html_info.find('img', {'class': 'teamlogo'}).get('src'),
        "location": re.sub('\s+', ' ', html_info.find_all('p')[2].text.replace('Location:', '').strip()),
        "seasons": re.sub('\s+', ' ', html_info.find_all('p')[4].text.replace('Seasons:', '').strip()),
        "all_time_record": re.sub('\s+', ' ', html_info.find_all('p')[5].text.replace('Record:', '').strip()),
        "current_record": re.sub('\s+', ' ', html_record.find('div', {'data-template': 'Partials/Teams/Summary'}).find('p').text.replace('Record:', '').strip()) if html_record else "",
        "playoff_appearances": re.sub('\s+', ' ', html_info.find_all('p')[6].text.replace('Playoff Appearances:', '').strip()),
        "championships": re.sub('\s+', ' ', html_info.find_all('p')[7].text.replace('Championships:', '').strip()),
        "all_seasons": new_nba_history,
        "current_roster": team_roster_data
    }

    return team_stats

# Fetch and parse season averages
def get_season_avgs():
    per_game_url = 'https://www.basketball-reference.com/leagues/NBA_stats_per_game.html'
    per_100_url = 'https://www.basketball-reference.com/leagues/NBA_stats_per_poss.html'

    soup_per_game = fetch_url_content(per_game_url)
    soup_per_100 = fetch_url_content(per_100_url)

    data_stats_per_game = [
        "ranker", "season", "lg_id", "age", "height", "weight", "g", "mp_per_g", "fg_per_g",
        "fga_per_g", "fg3_per_g", "fg3a_per_g", "ft_per_g", "fta_per_g", "orb_per_g",
        "drb_per_g", "trb_per_g", "ast_per_g", "stl_per_g", "blk_per_g", "tov_per_g",
        "pf_per_g", "pts_per_g", "fg_pct", "fg3_pct", "ft_pct", "pace", "efg_pct",
        "tov_pct", "orb_pct", "ft_rate", "off_rtg"]
    data_stats_per_poss = [
        "ranker", "season", "lg_id", "age", "height", "weight", "g", "fg_per_poss", "fga_per_poss",
        "fg3_per_poss", "fg3a_per_poss", "ft_per_poss", "fta_per_poss", "orb_per_poss", "drb_per_poss",
        "trb_per_poss", "ast_per_poss", "stl_per_poss", "blk_per_poss", "tov_per_poss", "pf_per_poss",
        "pts_per_poss", "fg_pct", "fg3_pct", "ft_pct", "pace", "efg_pct", "tov_pct", "orb_pct", "ft_rate",
        "off_rtg"]

    def get_data(table, stats):
        rows = table.find_all('tr')[2:]
        return [parse_data(row, stats) for row in rows if row.parent.name != 'tfoot']

    return {
        "NBA_averages_per_game": get_data(soup_per_game.find('table', {'id': 'stats'}), data_stats_per_game),
        "NBA_averages_per_100": get_data(soup_per_100.find('table', {'id': 'stats'}), data_stats_per_poss),
    }

# Fetch and parse player data by letter
def get_all_players_data(letter):
    url = f"https://www.basketball-reference.com/players/{letter}/"
    soup = fetch_url_content(url)
    html_players_table = soup.find('table', {'id': 'players'})

    def parse_players_table(table):
        rows = table.find_all('tr')[1:]
        players_dict = {}
        for row in rows:
            player_id = row.th['data-append-csv']
            player_data = parse_data(row, ["player", "year_min", "year_max", "pos", "height", "weight", "birth_date", "colleges"])
            player_data['id'] = player_id
            players_dict[player_data["player"]] = player_data
        return players_dict

    player_data = parse_players_table(html_players_table)
    return player_data

# Fetch and parse player data for all letters
def get_all_players_data_for_all_letters():
    players_data = {}  # Initialize the dictionary here
    for letter in string.ascii_lowercase:
        print(f"Fetching data for players starting with '{letter}'...")
        player_data = get_all_players_data(letter)
        players_data[letter] = player_data
        time.sleep(3)
    return players_data

# Fetch and parse individual player data
def get_player_data(player_id):
    def get_data(table, stats):
        rows = table.find_all('tr')[1:]
        return [parse_data(row, stats) for row in rows if row.parent.name != 'tfoot']

    def get_stats_table(soup, id, stats):
        div = soup.find('div', {'id': id})
        tables = find_commented_tables(div)
        return {table.get('id'): get_data(table, stats) for table in tables}

    def get_image(soup):
        img_tag = soup.find('img', {'itemscope': 'image'})
        return img_tag.get('src') if img_tag else None

    def get_and_cleanup_stats_table(soup, table_id, data_stats, cleanup=False):
        stats_table = get_stats_table(soup, table_id, data_stats)
        if cleanup:
            for key in stats_table:
                if stats_table[key]:
                    stats_table[key].pop(0)
        return stats_table

    def parse_table_to_list(table):
        data_list = []
        rows = table.find_all('tr')
        for row in rows:
            row_text = ' '.join(row.stripped_strings)
            data_list.append(row_text)
        return data_list

    def parse_commented_divs_to_dict(divs):
        div_dict = {}
        for div in divs:
            div_id = div.get('id', '')
            table = div.find('table')
            if table:
                div_dict[div_id] = parse_table_to_list(table)
        return div_dict

    url = f'https://www.basketball-reference.com/players/{player_id[0]}/{player_id}.html'

    try:
        soup = fetch_url_content(url)
    except Exception as e:
        logging.error(f"Error fetching or parsing URL {url}: {e}")
        return {"error": f"Could not fetch or parse data for player {player_id}"}

    data_stats_per_game = [
        "season", "age", "team_id", "lg_id", "pos", "g", "gs", "mp_per_g", "fg_per_g", "fga_per_g", "fg_pct", "fg3_per_g",
        "fg3a_per_g", "fg3_pct", "fg2_per_g", "fg2a_per_g", "fg2_pct", "efg_pct", "ft_per_g", "fta_per_g", "ft_pct", "orb_per_g",
        "drb_per_g", "trb_per_g", "ast_per_g", "stl_per_g", "blk_per_g", "tov_per_g", "pf_per_g", "pts_per_g"]
    data_stats_per_minute = [
        'season', 'age', "team_id", "lg_id", "pos", "g", "gs", "mp", "fg_per_mp", "fga_per_mp", "fg_pct", "fg3_per_mp",
        "fg3a_per_mp", "fg3_pct", "fg2_per_mp", "fg2a_per_mp", "fg2_pct", "ft_per_mp", "fta_per_mp", "ft_pct", "orb_per_mp",
        "drb_per_mp", "trb_per_mp", "ast_per_mp", "stl_per_mp", "blk_per_mp", "tov_per_mp", "pf_per_mp", "pts_per_mp"]
    data_stats_per_poss = [
        "season", "age", "team_id", "lg_id", "pos", "g", "gs", "mp", "fg_per_poss", "fga_per_poss",
        "fg_pct", "fg3_per_poss", "fg3a_per_poss", "fg3_pct", "fg2_per_poss", "fg2a_per_poss", "fg2_pct",
        "ft_per_poss", "fta_per_poss", "ft_pct", "orb_per_poss", "drb_per_poss", "trb_per_poss", "ast_per_poss", "stl_per_poss",
        "blk_per_poss", "tov_per_poss", "pf_per_poss", "pts_per_poss", "off_rtg", "def_rtg"]
    data_stats_advance = [
        'season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'mp', 'per', 'ts_pct', 'fg3a_per_fga_pct',
        'fta_per_fga_pct', 'orb_pct', 'drb_pct', 'trb_pct', 'ast_pct', 'stl_pct', 'blk_pct',
        'tov_pct', 'usg_pct', 'DUMMY', 'ows', 'dws', 'ws', 'ws_per_48', 'DUMMY', 'obpm', 'dbpm',
        'bpm', 'vorp']
    data_stat_adjusted_shooting = [
        'season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'mp', 'DUMMY', 'fg_pct', 'fg2_pct', 'fg3_pct',
        'efg_pct', 'ft_pct', 'ts_pct', 'fta_per_fga_pct', 'fg3a_per_fga_pct', 'DUMMY', 'lg_fg_pct', 'lg_fg2_pct',
        'lg_fg3_pct', 'lg_efg_pct', 'lg_ft_pct', 'lg_ts_pct', 'lg_fta_per_fga_pct', 'lg_fg3a_per_fga_pct', 'DUMMY',
        'adj_fg_pct', 'adj_fg2_pct', 'adj_fg3_pct', 'adj_efg_pct', 'adj_ft_pct', 'adj_ts_pct', 'adj_fta_per_fga_pct',
        'adj_fg3a_per_fga_pct', 'DUMMY', 'fg_pts_added', 'ts_pts_added']
    data_stats_play_by_play = [
        'season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'mp', 'pct_1', 'pct_2', 'pct_3', 'pct_4', 'pct_5',
        'plus_minus_on', 'plus_minus_net', 'tov_bad_pass', 'tov_lost_ball', 'fouls_shooting', 'fouls_offensive',
        'drawn_shooting', 'drawn_offensive', 'astd_pts', 'and1s', 'own_shots_blk']
    data_stats_shooting = [
        'season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'mp', 'fg_pct', 'avg_dist', 'DUMMY',
        'pct_fga_fg2a', 'pct_fga_00_03', 'pct_fga_03_10', 'pct_fga_10_16', 'pct_fga_16_xx', 'pct_fga_fg3a', 'DUMMY',
        'fg_pct_fg2a', 'fg_pct_00_03', 'fg_pct_03_10', 'fg_pct_10_16', 'fg_pct_16_xx', 'fg_pct_fg3a', 'DUMMY',
        'pct_ast_fg2', 'pct_ast_fg3', 'DUMMY', 'pct_fga_dunk', 'fg_dunk', 'DUMMY', 'pct_fg3a_corner3', 'fg_pct_corner3',
        'DUMMY', 'fg3a_heave', 'fg3_heave']
    data_stat_totals = [
        "season", "age", "team_id", "lg_id", "pos", "g", "gs", "mp", "fg", "fga",
        "fg_pct", "fg3", "fg3a", "fg3_pct", "fg2", "fg2a", "fg2_pct", "efg_pct",
        "ft", "fta", "ft_pct", "orb", "drb", "trb", "ast", "stl", "blk", "tov", "pf", "pts", "DUMMY", "trp_dbl"]

    data = {}

    try:
        data["image"] = get_image(soup)
    except Exception as e:
        logging.error(f"Error getting image: {e}")

    try:
        data["per_game_regular_season"] = get_data(
            soup.find('table', {'id': 'per_game'}), data_stats_per_game)
    except Exception as e:
        logging.error(f"Error getting per_game_regular_season data: {e}")

    try:
        data["per_game_playoff"] = get_data(
            soup.find('table', {'id': 'playoffs_per_game'}), data_stats_per_game)
    except Exception as e:
        logging.error(f"Error getting per_game_playoff data: {e}")

    try:
        data["advanced_regular_season"] = get_data(
            soup.find('table', {'id': 'advanced'}), data_stats_advance)
    except Exception as e:
        logging.error(f"Error getting advanced_regular_season data: {e}")

    try:
        data["advanced_regular_playoff"] = get_data(
            soup.find('table', {'id': 'playoffs_advanced'}), data_stats_advance)
    except Exception as e:
        logging.error(f"Error getting advanced_regular_playoff data: {e}")

    try:
        stats_tables_per_minute = get_and_cleanup_stats_table(
            soup, 'all_per_minute-playoffs_per_minute', data_stats_per_minute)
        data["per_36_regular_season"] = stats_tables_per_minute.get(
            'per_minute')
        data["per_36_playoff"] = stats_tables_per_minute.get(
            'playoffs_per_minute')
    except Exception as e:
        logging.error(f"Error getting per_36 data: {e}")

    try:
        stats_tables_per_poss = get_and_cleanup_stats_table(
            soup, 'all_per_poss-playoffs_per_poss', data_stats_per_poss)
        data["per_100_regular_season"] = stats_tables_per_poss.get('per_poss')
        data["per_100_playoff"] = stats_tables_per_poss.get(
            'playoffs_per_poss')
    except Exception as e:
        logging.error(f"Error getting per_100 data: {e}")

    try:
        stats_tables_all_adj_shooting = get_and_cleanup_stats_table(
            soup, 'all_adj_shooting', data_stat_adjusted_shooting, cleanup=True)
        data["adjusted_shooting_regular_season"] = stats_tables_all_adj_shooting.get(
            "adj_shooting")
    except Exception as e:
        logging.error(f"Error getting adjusted_shooting data: {e}")

    try:
        stats_tables_play_by_play = get_and_cleanup_stats_table(
            soup, 'all_pbp-playoffs_pbp', data_stats_play_by_play, cleanup=True)
        data["play_by_play_regular_season"] = stats_tables_play_by_play.get(
            "pbp")
        data["play_by_play_playoff"] = stats_tables_play_by_play.get(
            "playoffs_pbp")
    except Exception as e:
        logging.error(f"Error getting play_by_play data: {e}")

    try:
        stats_tables_shooting = get_and_cleanup_stats_table(
            soup, 'all_shooting-playoffs_shooting', data_stats_shooting, cleanup=True)
        data["shooting_regular_season"] = stats_tables_shooting.get("shooting")
        data["shooting_playoff"] = stats_tables_shooting.get(
            "playoffs_shooting")
    except Exception as e:
        logging.error(f"Error getting shooting data: {e}")

    try:
        data["totals_regular_season"] = get_data(
            soup.find('table', {'id': 'totals'}), data_stat_totals)
    except Exception as e:
        logging.error(f"Error getting totals_regular_season data: {e}")

    try:
        data["totals_playoffs"] = get_data(
            soup.find('table', {'id': 'playoffs_totals'}), data_stat_totals)
    except Exception as e:
        logging.error(f"Error getting totals_playoffs data: {e}")

    try:
        div_leaderboard = soup.find('div', {'id': 'all_leaderboard'})
        commented_divs = find_commented_divs(div_leaderboard)
        data["awards_honors"] = parse_commented_divs_to_dict(commented_divs)
    except Exception as e:
        logging.error(f"Error getting awards_honors data: {e}")

    return data
