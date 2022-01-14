import requests
from bs4 import BeautifulSoup as bs
import datetime
import time
import sys

MONTH_DICT = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
RINK_FREMONT = "Fremont"
LOC_FREMONT  = "Solar4America Ice at Fremont, 44388 Old Warm Springs Blvd, Fremont, CA 94538, USA"
LOC_SJ       = "Solar4America Ice, 1500 S 10th St, San Jose, CA 95112, USA"

class Game:
    def __init__(self, game, teamname):
        self.teamname        = teamname
        self.start, self.end = getGameTimes(game)
        self.location        = LOC_FREMONT if game['Rink'] == RINK_FREMONT else LOC_SJ
        self.rink            = RINK_FREMONT if game['Rink'] == RINK_FREMONT else game['Rink'].split(' ')[2]
        self.jersey          = 'Light' if game['Home'] == teamname else 'Dark'
        self.is_past         = self.start < datetime.datetime.now()
        self.summary         = f"{teamname} - {self.rink} - {self.jersey}"
        self.result          = getGameResult(game, self.is_past, teamname)
        self.description     = f'{teamname} [{game["idx"]}] {game["Type"]}'
    
    def getStartFmt(self):
        t = self.start
        return "{}-{}-{}T{:02d}:{:02d}:00-08:00".format(t.year, t.month, t.day, t.hour, t.minute)

    def getEndFmt(self):
        t = self.end
        return "{}-{}-{}T{:02d}:{:02d}:00-08:00".format(t.year, t.month, t.day, t.hour, t.minute)

    def __str__(self):
        return f'{self.getStartFmt()} {self.rink} {self.result}'

def read_all_games(teamname, url):
    s = requests.session()
    games_page = s.get(url)

    soup   = bs(games_page.text, 'html.parser')
    table  = soup.find('table')

    header = table.contents[1]
    header_items = [item.text for item in header.contents]

    games = []
    for idx, game in enumerate(table.contents[2:]):
        game_items = [item.text.strip() for item in game.contents]
        new_game = {key:value for key, value in zip(header_items, game_items)}
        home_goals = game_items[9].strip()
        away_goals = game_items[7].strip()
        new_game['was_shootout'] = 'S' in home_goals or 'S' in away_goals
        new_game['home_goals'] = 0 if home_goals == "" else int(home_goals.split(' ')[0])
        new_game['away_goals'] = 0 if away_goals == "" else int(away_goals.split(' ')[0])
        new_game['idx'] = idx
        games.append(Game(new_game, teamname))
    return games

def getGameResult(game, is_past, teamname):
    if is_past:
        if game['Home'] == teamname:
            goals_for     = game['home_goals']
            goals_against = game['away_goals']
        else:
            goals_for     = game['away_goals']
            goals_against = game['home_goals']
        if goals_for > goals_against:
            res = 'W'
        elif goals_for < goals_against:
            res = 'L'
        else:
            res = 'T'
        if game['was_shootout']:
            res += 'SO'
        return f'{teamname} {res} {goals_for}-{goals_against}'
    else:
        return 'TBD'

def getMonthNum(m):
    if m in MONTH_DICT.keys():
        return MONTH_DICT[m]
    print("!!!!! Bad month: {}".format(m))
    sys.exit(1)

def isDuringDaylightSavingsTime(year, month, day, hours, minutes):
    time_dt = datetime.datetime(year, month, day, hours, minutes)
    time_sec = time.mktime(time_dt.timetuple())
    time_local = time.localtime(time_sec)
    return time_local.tm_isdst

def getGameTimes(game):
    # From 'Mon Nov 13 08:00 PM' to '2017-11-13T20:00:00-08:00'
    time, ampm = game['Time'].split(' ')
    hours, minutes = [int(x) for x in time.split(':')]

    _, month, day = game['Date'].split(' ')
    day = int(day)
    month = getMonthNum(month)

    now = datetime.datetime.now()
    year = int(now.year)
    if month < now.month:
        year += 1
    hours = int(hours)
    minutes = int(minutes)
    if ampm == "PM" and hours != 12:
        hours += 12
    if isDuringDaylightSavingsTime(year, month, day, hours, minutes):
        hours -= 1

    start = datetime.datetime(year, month, day, hours, minutes)
    return [start, start + datetime.timedelta(hours=1, minutes=30)]

if __name__ == "__main__":
    [print(game) for game in read_all_games("Stampede", "https://stats.sharksice.timetoscore.com/display-schedule?team=53&league=1&stat_class=1")]