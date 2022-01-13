import googlecalendar
import siahl

TEAMS = [
    {'name':'Stampede',   'url':'https://stats.sharksice.timetoscore.com/display-schedule?team=53&league=1&stat_class=1'},
    {'name':'Gang Green', 'url':'https://stats.sharksice.timetoscore.com/display-schedule?team=79&league=1&stat_class=1'}
]

def main():
    cal = googlecalendar.GoogleCalendar()
    for team in TEAMS:
        print(f"Updating {team['name']} schedule:")
        games = siahl.read_all_games(team['name'], team['url']) 
        upcoming_games = [game for game in games if not game.is_past]
        past_games     = [game for game in games if game.is_past]
        cal.add_upcoming_games(upcoming_games)
        cal.update_past_games (past_games)

if __name__ == "__main__":
    main()