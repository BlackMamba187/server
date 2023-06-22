from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)
CORS(app)

@app.route('/activeteams', methods=['GET'])
def get_players():
    def parse_row(row):
        team_name = row.th.text
        team_data = {
            'Lg': row.find('td', {'data-stat': 'lg_id'}).text,
            'From': row.find('td', {'data-stat': 'year_min'}).text,
            'To': row.find('td', {'data-stat': 'year_max'}).text,
            'Yrs': row.find('td', {'data-stat': 'years'}).text,
            'Games': row.find('td', {'data-stat': 'g'}).text,
            'Wins': row.find('td', {'data-stat': 'wins'}).text,
            'Losses': row.find('td', {'data-stat': 'losses'}).text,
            'Win_Loss_Percentage': row.find('td', {'data-stat': 'win_loss_pct'}).text,
            'Plyfs': row.find('td', {'data-stat': 'years_playoffs'}).text,
            'Div': row.find('td', {'data-stat': 'years_division_champion'}).text,
            'Conf': row.find('td', {'data-stat': 'years_conference_champion'}).text,
            'Champ': row.find('td', {'data-stat': 'years_league_champion'}).text,
        }
        return team_name, team_data

    def parse_table(html_table):
        soup = BeautifulSoup(html_table, 'html.parser')
        rows = soup.find_all('tr')

        franchise_data = {}
        for row in rows:
            if row.has_attr('class') and 'full_table' in row['class']:
                franchise_name, franchise_info = parse_row(row)
                franchise_data[franchise_name] = {'Current': franchise_info, 'History': {}}
            elif row.has_attr('class') and 'partial_table' in row['class']:
                team_name, team_info = parse_row(row)
                if franchise_name in franchise_data:
                    franchise_data[franchise_name]['History'][team_name] = team_info

        return franchise_data

    url = 'https://www.basketball-reference.com/teams/'
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    html_table = str(soup.find('table', {'id': 'teams_active'}))

    franchise_data = parse_table(html_table)
    return jsonify(franchise_data)

if __name__ == '__main__':
    app.run(debug=True)
