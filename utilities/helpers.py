import requests
from bs4 import BeautifulSoup, Comment
import datetime


def get_current_season_year():
    now = datetime.datetime.now()
    return now.year


def generate_nba_history():
    nba_history = []
    decades = range(1940, 2030, 10)  # Generate decades from 1940 to 2020s

    for decade in decades:
        decade_label = f"{decade}s"
        years = [
            f"{year}-{str(year + 1)[-2:]}" for year in range(decade, decade + 10)]
        if decade == 2020:
            current_year = get_current_season_year()
            years[-1] = f"{current_year}-{str(current_year + 1)[-2:]}"
        nba_history.append({decade_label: years})

    return nba_history


def fetch_url_content(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')


def parse_data(row, stats_list):
    parsed_data = {}
    for stat in stats_list:
        cell = row.find(['td', 'th'], {'data-stat': stat})
        if cell is not None:
            parsed_data[stat] = cell.text.strip()
        else:
            parsed_data[stat] = ''
    return parsed_data


def find_commented_tables(soup):
    tables = []
    comments = soup.find_all(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment_soup = BeautifulSoup(comment, 'html.parser')
        table = comment_soup.find_all('table')
        if table:
            tables.extend(table)
    return tables


def find_commented_divs(soup):
    divs = []
    comments = soup.find_all(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment_soup = BeautifulSoup(comment, 'html.parser')
        div = comment_soup.find_all('div', id=True)
        if div:
            divs.extend(div)
    return divs
