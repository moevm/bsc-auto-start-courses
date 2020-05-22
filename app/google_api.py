# Test example from google

import os
import flask
import requests

from flask import Flask, render_template, flash, redirect, session, url_for, request, g, Markup
import datetime

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# for FlaskForm
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

# for mongodb
from pymongo import MongoClient

from app import app

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
# CLIENT_SECRETS_FILE = "client_secret_new_web_app1.json"
CLIENT_SECRETS_FILE = "/var/www/apache-flask/app/client_secret_new_web_app1.json"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/script.send_mail', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
API_SERVICE_NAME = 'script'
API_VERSION = 'v1'

### app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

app.config.update(dict(
  SECRET_KEY="powerful secretkey",
  WTF_CSRF_SECRET_KEY="a csrf secret key"
))

class CreatingForm(FlaskForm):
  name = StringField('Название таблицы', validators=[DataRequired()])
  emails = StringField('emails (вводить через запятую)', validators=[DataRequired()])
  groups = StringField('groups (enter comma-separated)', validators=[DataRequired()])

class CreatingSheets(FlaskForm):
  sheet_id = SelectField('Таблица ответов',  choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])

class CreatingRepo(FlaskForm):
  subject = StringField('subject', validators=[DataRequired()])
  group = StringField('group', validators=[DataRequired()])

# Для работы с БД
# class UserDetails(FlaskForm):
#   sheet_id = SelectField('Таблица ответов', coerce=int)

# def edit_user(request, id):
#     user = User.query.get(id)
#     form = UserDetails(request.POST, obj=user)
#     form.group_id.choices = [(g.id, g.name) for g in Group.query.order_by('name')]

client = MongoClient('localhost', 27017)
db = client.ssdb

@app.route('/')
@app.route('/index')
def index():
  form = CreatingForm()
  sheetsForm = CreatingSheets()
  gitForm = CreatingRepo()
  _items_tables = db.answers.find()
  items_tables = [item for item in _items_tables]
  _items_groups = db.groups.find()
  items_groups = [item for item in _items_groups]
  _items_githubs = db.github.find()
  items_githubs = [item for item in _items_githubs]
  now = datetime.datetime.now()
  year = now.year
  return render_template('index.html', form=form, items_tables=items_tables, items_groups=items_groups, items_githubs=items_githubs, year=year)
  # return print_index_table()


@app.route('/test', methods=['POST'])
def test_api_request():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  drive = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # service = get_scripts_service()
    # # API ID from step 3 in Google Sheets/Script section
  API_ID = "MwNcL5k4su6HQgR_MGSBhaEiAo2eQ3wDV"
  SCRIPT_ID = "1xeBCg0u5RHuBEix-I_I9vdNMH-MOUWo3M9yqYfzzgwxHIasrT9kNoqh3"
  # print('good')
  table_name = request.form['name']
  list_of_groups = request.form['groups'].split(',')
  # # Instead macro_test select your macro function name 
  # # from step 5 in Sheets/Script section
  testmail = request.form['emails']
  body = {"function": "createForm", "devMode": True,
          "parameters": testmail} 

  # try:
  response = drive.scripts().run(body=body, scriptId=SCRIPT_ID).execute()
  item_of_db = {
    'name': table_name,
    'list_of_groups': list_of_groups,
    'table_id': response['response']['result']
  }
  db.answers.insert_one(item_of_db)

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)

  # return flask.jsonify(**files)
  return redirect(url_for('index'))

@app.route('/fill-db')
def fill_db():
  # another_item_of_db = {
  #   'name': "test table test",
  #   'list_of_groups': [6381, 6382],
  #   'table_id': '13-7o2vG41cjKmbushJlgncHQlAL-a1TPL4HFGIMLvV0'
  # }
  d# db.groups.insert_one({'group': 6381,
  #                         'table_id': '1nCdFRoLyiP5gNNbi2dR_Z-y4w5KxGWdACcjr5oHmpnI'})
  db.github.insert_one({
    'repo': 'ooop-2020-6381',
    'group': '6381',
    'table_id': '1nCdFRoLyiP5gNNbi2dR_Z-y4w5KxGWdACcjr5oHmpnI'
  })
  return redirect(url_for('index'))

@app.route('/make-spreadsheets', methods=['POST'])
def make_spredsheets():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')
  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  # spreadsheet_id = '13-7o2vG41cjKmbushJlgncHQlAL-a1TPL4HFGIMLvV0'
  spreadsheet_id = request.form['table']
  tmpel = db.answers.find({'table_id': spreadsheet_id})
  items = [item for item in tmpel]
  ss = googleapiclient.discovery.build(
      'sheets', 'v4', credentials=credentials)
  
  # Пример чтения файла
  values = ss.spreadsheets().values().get(
      spreadsheetId=spreadsheet_id,
      range='A1:I20',
      majorDimension='ROWS'
  ).execute()
  # pprint(values)
  # first_group = values['values'][1]

  testList = items[0]['list_of_groups']
  testDict = {}
  testSS = {}

  # создание таблиц для групп
  for i in range(len(testList)):
    testSS[testList[i]] = ss.spreadsheets().create(body = {
    'properties': {'title': 'Тестовый документ ' + str(testList[i]), 'locale': 'ru_RU'}
    }).execute()
    tmpSSId = testSS[testList[i]].get('spreadsheetId')
    # d = {}
    # d[testList[i]] = tmpSSId
    db.groups.insert_one({'group': (testList[i]),
                          'table_id': tmpSSId})
    # print(tmpSSId)
    add_info_in_table = ss.spreadsheets().values().batchUpdate(spreadsheetId = tmpSSId, body = {
    "valueInputOption": "USER_ENTERED",
    "data": [
        {"range": "Лист1!A1:D1",
         "majorDimension": "ROWS",     # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
         "values": [['ФИО', 'github', 'stepik', 'email']]},
    ]
    }).execute()

  for i in range(len(testList)):
    testDict[testList[i]] = []
    for row in values['values']:
      if row[4] == str(testList[i]):
        testDict[testList[i]].append([row[1] + ' ' + row[2] + ' ' + row[3], row[7], row[8], row[6]])
    tmpSSId = testSS[testList[i]].get('spreadsheetId')
    results = ss.spreadsheets().values().batchUpdate(spreadsheetId = tmpSSId, body = {
    "valueInputOption": "USER_ENTERED",
    "data": [
        {"range": "Лист1!A2:D10",
         "majorDimension": "ROWS",     # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
         "values": testDict[testList[i]]},
    ]
    }).execute()
  
  return redirect(url_for('index'))

@app.route('/bd')
def search_element():
  # tmpel = db.answers.find({'name': "test table"})
  # tmpel = db.answers.find({'table_id': '13-7o2vG41cjKmbushJlgncHQlAL-a1TPL4HFGIMLvV0'})
  # items = [item for item in tmpel]
  # return items[0]['name']
  # spreadsheet_id = request.form['table']
  tmpel = db.groups.find()
  items = [item for item in tmpel]
  return str(items)

@app.route('/test-ss')
def spreadsheets():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  spreadsheet_id = '13-7o2vG41cjKmbushJlgncHQlAL-a1TPL4HFGIMLvV0'
  ss = googleapiclient.discovery.build(
      'sheets', 'v4', credentials=credentials)
  
  # Пример чтения файла, необходимо менять размерности
  values = ss.spreadsheets().values().get(
      spreadsheetId=spreadsheet_id,
      range='A1:I3',
      majorDimension='ROWS'
  ).execute()
  print(values)
  return str(values)

@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)# так как с этой байдой по http не работает

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('index'))


@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')
