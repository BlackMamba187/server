from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS

from utilities.scrape import (get_active_teams, get_team_info, get_all_players_data, get_all_players_data_for_all_letters,
                              get_player_data, get_season_avgs)

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NBA Web Service</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }
            h1 {
                color: #333;
            }
            p {
                margin-bottom: 20px;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin-bottom: 10px;
            }
            a {
                text-decoration: none;
                color: #007BFF;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to our NBA Web Service!</h1>
        <p>Use the following routes to access various NBA data:</p>
        <ul>
            <li><a href="">/seasonavg</a> - Get season averages</li>
            <li><a href="">/activeteams</a> - Get active teams in the NBA and their history</li>
            <li><a href="">/team/&lt;team_id&gt;</a> - Get specific team information (replace <strong>&lt;team_id&gt;</strong> with the team's ID from the active teams)</li>
            <li><a href="">/players</a> - Get all players ever</li>
            <li><a href="">/player/&lt;player_id&gt;</a> - Get specific player data (replace <strong>&lt;player_id&gt;</strong> with the player's ID)</li>
        </ul>
    </body>
    </html>
    """
    return render_template_string(html_content)


@app.route('/seasonavg', methods=['GET'])
def season_avg():
    data = get_season_avgs()
    return data
    
@app.route('/activeteams', methods=['GET'])
def active_teams_json():
    data = get_active_teams()
    return data

@app.route('/team/<team_id>', methods=['GET'])
def get_team_info_json(team_id):
    data = get_team_info(team_id)
    return data

@app.route('/players/', methods=['GET'])
def get_all_players_data_for_all_letters_json():
    data = get_all_players_data_for_all_letters()
    return data

@app.route('/player/<player_id>', methods=['GET'])
def get_player_data_json(player_id):
    data = get_player_data(player_id)
    return data

@app.route('/players/batch', methods=['POST'])
def get_player_data_batch():
    player_ids = request.json.get('player_ids', [])
    results = {}
    for player_id in player_ids:
        player_data = get_player_data(player_id)
        results[player_id] = player_data
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
