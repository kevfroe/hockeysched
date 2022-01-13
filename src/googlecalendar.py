from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendar:
    def __init__(self):
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_game_event(self, game):
        eventsResult = self.service.events().list(
            calendarId='primary',
            timeMin=game.getStartFmt(),
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = eventsResult.get('items', [])

        if events:
            for event in events:
                if 'description' in event.keys() and event['description'] == game.description:
                    return event
        return None

    def add_upcoming_games(self, games):
        try:
            for game in games:
                print("\tChecking on upcoming game: {} - {}, {}... ".format(game.teamname, game.rink, game.getStartFmt()), end="")

                if _ := self.get_game_event(game):
                    print("Game already exists in calendar.")
                else:
                    print("Game does not exist in calendar. Adding game now. ", end="")
                    ret_event = self.service.events().insert(calendarId='primary', body={
                        'summary': game.summary,
                        'location': game.location,
                        'description':game.description,
                        'start': {
                            'dateTime': game.getStartFmt(),
                            'timeZone': "America/Los_Angeles",
                        },
                        'end': {
                            'dateTime': game.getEndFmt(),
                            'timeZone': "America/Los_Angeles",
                        },
                    }).execute()
                    print("Status: {}".format(ret_event['status']))

        except HttpError as error:
            print('An error occurred: %s' % error)

    def update_past_games(self, games):
        try:
            for game in games:
                print("\tUpdating past game: {} - {}, {}... ".format(game.teamname, game.rink, game.getStartFmt()), end="")

                if event := self.get_game_event(game):
                    event['summary'] = game.result
                    ret_event = self.service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                    print("Status: {}".format(ret_event['status']))

                else:
                    print("Game does not exist in calendar. Adding game now. ", end="")
                    ret_event = self.service.events().insert(calendarId='primary', body={
                        'summary': game.result,
                        'location': game.location,
                        'description':game.description,
                        'start': {
                            'dateTime': game.getStartFmt(),
                            'timeZone': "America/Los_Angeles",
                        },
                        'end': {
                            'dateTime': game.getEndFmt(),
                            'timeZone': "America/Los_Angeles",
                        },
                    }).execute()
                    print("Status: {}".format(ret_event['status']))

        except HttpError as error:
            print('An error occurred: %s' % error)

if __name__ == "__main__":
    cal = GoogleCalendar()
    #cal.read_events(10)