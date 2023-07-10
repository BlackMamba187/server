import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from .settings import team_ids

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