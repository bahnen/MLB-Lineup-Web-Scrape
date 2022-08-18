import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


def get_players(home_away_dict):
    rows = []
    for home_away, v in home_away_dict.items():
        players = v['players']
        print("\n{} - {}".format(v['team'], v['lineupStatus']))
        for idx, player in enumerate(players):
            if home_away == 'Home':
                team = home_away_dict['Home']['team']
                opp = home_away_dict['Away']['team']
            else:
                team = home_away_dict['Away']['team']
                opp = home_away_dict['Home']['team']
            if player.find('span', {'class': 'lineup__throws'}):
                playerPosition = 'P'
                handedness = player.find('span', {'class': 'lineup__throws'}).text
            else:
                playerPosition = player.find('div', {'class': 'lineup__pos'}).text
                handedness = player.find('span', {'class': 'lineup__bats'}).text

            if 'title' in list(player.find('a').attrs.keys()):
                playerName = player.find('a')['title'].strip()
            else:
                playerName = player.find('a').text.strip()

            playerRow = {
                'Bat Order': idx,
                'Name': playerName,
                'Position': playerPosition,
                'Team': team,
                'Opponent': opp,
                'Home/Away': home_away,
                'Handedness': handedness,
                'Lineup Status': home_away_dict[home_away]['lineupStatus']}

            rows.append(playerRow)
            print('{} {}'.format(playerRow['Position'], playerRow['Name']))

    return rows


rows = []
url = 'https://www.rotowire.com/baseball/daily-lineups.php'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
lineupBoxes = soup.find_all('div', {'class': 'lineup__box'})

for lineupBox in lineupBoxes:
    try:
        awayTeam = lineupBox.find('div', {'class': 'lineup__team is-visit'}).text.strip()
        homeTeam = lineupBox.find('div', {'class': 'lineup__team is-home'}).text.strip()

        print(f'\n\n############\n  {awayTeam} @ {homeTeam}\n############')

        awayLineup = lineupBox.find('ul', {'lineup__list is-visit'})
        homeLineup = lineupBox.find('ul', {'lineup__list is-home'})

        awayLineupStatus = awayLineup.find('li', {'class': re.compile('lineup__status.*')}).text.strip()
        homeLineupStatus = homeLineup.find('li', {'class': re.compile('lineup__status.*')}).text.strip()

        awayPlayers = awayLineup.find_all('li', {'class': re.compile('lineup__player.*')})
        homePlayers = homeLineup.find_all('li', {'class': re.compile('lineup__player.*')})

        home_away_dict = {
            'Home': {
                'team': homeTeam, 'players': homePlayers, 'lineupStatus': homeLineupStatus},
            'Away': {
                'team': awayTeam, 'players': awayPlayers, 'lineupStatus': awayLineupStatus}}

        playerRows = get_players(home_away_dict)
        rows += playerRows
    except:
        continue

df = pd.DataFrame(rows, columns=["Bat Order", "Name", "Position", "Team", "Opponent", "Home/Away", "Handedness", "Lineup Status"]
                  )
df.to_excel("MLB Prediction Lineup.xlsx", sheet_name='sheet1', index=False)
print(df.head(10).to_markdown(index=False))