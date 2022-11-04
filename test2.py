import os
from fastapi import FastAPI,Request
from starlette.middleware.sessions import SessionMiddleware
import requests
from fastapi.responses import RedirectResponse
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery



import flask

app = FastAPI()
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']



@app.get('/')
def test_api_request(req:Request):
  creds = None
  if 'credentials' in req.session:
    creds = google.oauth2.credentials.Credentials(
      **req.session.get('credentials',None))


    # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            #flow = InstalledAppFlow.from_client_secrets_file(
             #   'credentials.json', SCOPES)
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
              "credentials.json", scopes=SCOPES)

            #flow.redirect_uri = flask.url_for('/authorize', _external=True)
            flow.redirect_uri = "https://theruntime.software/auth"
            authorization_url, state = flow.authorization_url(
                # Enable offline access so that you can refresh an access token without
                # re-prompting the user for permission. Recommended for web server apps.
                access_type='offline',
                # Enable incremental authorization. Recommended as a best practice.
                include_granted_scopes='true')
            response = RedirectResponse(authorization_url)
            req.session['state'] = state 
            return response
  try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return
        resp_lis = ""
        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            resp_lis+=start, event['summary']+"\n"
        return resp_lis
  
  except HttpError as error:
        print('An error occurred: %s' % error)


@app.get('/auth')
def oauth2callback(state:str, code:str, scope:str, req:Request):
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = req.session.get('state',None)

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      "credentials.json", scopes=SCOPES, state=state)
  flow.redirect_uri = "https://theruntime.software/auth"

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = str(req.url)
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  req.session['credentials'] = credentials_to_dict(credentials)

  return RedirectResponse('/')





app.add_middleware(SessionMiddleware, secret_key="some-random-string")
