from flask import render_template, flash, redirect, session, url_for, request, g, Markup
import os
import flask
from app import app
from app import google_api
from flask_csv import send_csv

# for FlaskForm
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

from flask_dance.contrib.github import make_github_blueprint, github

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

API_ID = "MwNcL5k4su6HQgR_MGSBhaEiAo2eQ3wDV"
SCRIPT_ID = "1xeBCg0u5RHuBEix-I_I9vdNMH-MOUWo3M9yqYfzzgwxHIasrT9kNoqh3"

CLIENT_ID_GITHUB = 'b7642ad896f5597b5f6b'
CLIENT_SECRET_GITHUB = '14320921a9af8e0c15a1f2c59ea8eaae043f33e7'
SCOPES_GITHUN = 'admin:org,repo,user'

github_blueprint = make_github_blueprint(client_id=CLIENT_ID_GITHUB,
                                         client_secret=CLIENT_SECRET_GITHUB,
                                         scope=SCOPES_GITHUN)

app.register_blueprint(github_blueprint, url_prefix='/github_login')


@app.route('/test-github')
def github_login():
  if not github.authorized:
      return redirect(url_for('github.login'))
  else:
      account_info = github.get('/user')
      if account_info.ok:
          account_info_json = account_info.json()
          return '<h1>Your Github name is {}'.format(account_info_json['id'])

  return '<h1>Request failed!</h1>'

@app.route('/test-github-list-repo')
def get_list_repo():
  if not github.authorized:
        return redirect(url_for('github.login'))
  else:
      list_repo = github.get('/user/repos', params={"type": 'private'})
      # pprint(list_repo.json())
      return 'info in console'
  return 'smt bad'      

@app.route('/test-github-create-repo')
def create_repo():
  if not github.authorized:
        return redirect(url_for('github.login'))
  else:
      create_new_repo = github.post('/user/repos', json={"name": 'Hello-World-public', "description": 'This is your first repository'})
      # pprint(create_new_repo.json())
      return 'info in console'
  return 'smt bad'     

@app.route('/test-github-branch')
def get_branch():
  if not github.authorized:
        return redirect(url_for('github.login'))
  else:
      branch = github.get('/repos/spasartyom/coursera-frontend/branches/master/protection')
      # pprint(branch.json())
      return 'info in console'
  return 'smt bad'    

@app.route('/test-github-create-template-repo', methods=['POST'])
def create_template_repo():
  if not github.authorized:
        return redirect(url_for('github.login'))
  else:
      subject = request.form['subject']
      year = request.form['year']
      group = request.form['table']
      private = bool(int(request.form['private']))
      name = subject + '-' + year + '-' + group
      test_in = github.post('/orgs/test-for-docker/repos', json={"name": name, "private": private, "auto_init": 'true'})
      if test_in.status_code == 201:
        item_db = google_api.db.groups.find({'group': int(group)})
        items = [item for item in item_db]
        spreadsheet_id = items[0]['table_id']
        google_api.db.github.insert_one({
          'repo': name,
          'group': group,
          'table_id': spreadsheet_id
        })
        invite_team_one = github.put('/orgs/moevm/teams/cs-teacher/repos/moevm/' + name, json={"permission": 'admin'})
        invite_team_two = github.put('/orgs/moevm/teams/pr-teacher/repos/moevm/' + name, json={"permission": 'admin'})
        invite_info = github.put('/repos/moevm/' + name + '/collaborators/moevm-pull-requests-checker', json={"permission": 'admin'})
        add_protect_rule(name)
        data_csv = add_users(spreadsheet_id, name)
        return send_csv(data_csv,
                    "list_wrong_github.csv", ["FIO", "github", "email"])
        # if invite_team_info_rep.status_code == 204:
        #   return redirect(url_for('index'))
      
      # pprint(create_new_repo_by_template.json())
      # return redirect(url_for('index'))
      # return str(create_new_repo_by_template.json())
      return 'smt bad'
  return 'smt bad'

@app.route('/test-github-list-col', methods=['POST'])
def check_collab():
  if not github.authorized:
        return redirect(url_for('github.login'))
  else:
    repo_name = request.form['github']
    item_db = google_api.db.github.find({'repo': repo_name})
    items = [item for item in item_db]
    spreadsheet_id = items[0]['table_id']
    list_collab = github.get('/repos/test-for-docker/' + repo_name + '/invitations')
    # if list_collab.status_code == 204:
    #   return 'yes'
    # if list_collab.status_code == 404:
    #   return 'no'
    list_invitee = []
    for item in list_collab.json():
      list_invitee.append(item['invitee']['login'])

    data_csv = notificate_students(spreadsheet_id, repo_name, list_invitee)
    return send_csv(data_csv,
                    "list_github.csv", ["FIO", "github", "email"])

    # return redirect(url_for('index'))
  return 'smt bad'

@app.route('/test-github-invite')
def invite_user():
  if not github.authorized:
        return redirect(url_for('github.login'))
  else:
      invite_info = github.put('/repos/spasartyom/Hello-World-by-template/collaborators/username')
      # pprint(invite_info.json())
      return 'info in console'
  return 'smt bad'

def add_users(ss_id, rep_name):
  if 'credentials' not in google_api.flask.session:
    return google_api.flask.redirect('authorize')
  # Load credentials from the session.
  credentials = google_api.google.oauth2.credentials.Credentials(
      **google_api.flask.session['credentials'])

  ss = google_api.googleapiclient.discovery.build(
      'sheets', 'v4', credentials=credentials)
  
  # spreadsheetId='1nCdFRoLyiP5gNNbi2dR_Z-y4w5KxGWdACcjr5oHmpnI',
  # Пример чтения файла
  response_ss = ss.spreadsheets().values().get(
      spreadsheetId=ss_id,
      range='A1:I20',
      majorDimension='COLUMNS'
  ).execute()
  values = response_ss['values'][1]
  list_emails = response_ss['values'][3]
  list_fio = response_ss['values'][0]

  notfound = []
  final_data = []

  for i in range(1, len(values)):
    invite_info = github.put('/repos/moevm/' + rep_name + '/collaborators/' + values[i])
    if invite_info.status_code == 404:
      notfound.append(list_emails[i])
      final_data.append({'FIO': list_fio[i], 'github': values[i], 'email': list_emails[i]})
    
  notfound_emails = ','.join(notfound)

  script = google_api.googleapiclient.discovery.build(
      'script', 'v1', credentials=credentials)
  
  # API_ID = "MwNcL5k4su6HQgR_MGSBhaEiAo2eQ3wDV"
  # SCRIPT_ID = "1xeBCg0u5RHuBEix-I_I9vdNMH-MOUWo3M9yqYfzzgwxHIasrT9kNoqh3"
  body = {"function": "sendMail", "devMode": True,
          "parameters": notfound_emails}
  response = script.scripts().run(body=body, scriptId=SCRIPT_ID).execute()
  return final_data


def add_protect_rule(rep_name):
  rule_protect = {
    "required_status_checks": None,
    "enforce_admins": None,
    "required_pull_request_reviews": None,
    "restrictions": {
      "users": [
        "moevm-pull-requests-checker"
      ],
      "teams": [
        "cs_teachers",
        "pr_teachers"
      ]
    }
  }
  new_branch = github.put('/repos/moevm/' + rep_name + '/branches/master/protection', json=rule_protect)

def notificate_students(ss_id, repo_name, list_invitee):
  if 'credentials' not in google_api.flask.session:
      return google_api.flask.redirect('authorize')
  # Load credentials from the session.
  credentials = google_api.google.oauth2.credentials.Credentials(
      **google_api.flask.session['credentials'])

  ss = google_api.googleapiclient.discovery.build(
      'sheets', 'v4', credentials=credentials)
  
  # spreadsheet_Id='1nCdFRoLyiP5gNNbi2dR_Z-y4w5KxGWdACcjr5oHmpnI',
  # чтения файла
  response_ss = ss.spreadsheets().values().get(
      spreadsheetId=ss_id,
      range='A1:I20',
      majorDimension='COLUMNS'
  ).execute()
  list_fio = response_ss['values'][0]
  values = response_ss['values'][1]
  list_emails = response_ss['values'][3]

  final_emails = []
  final_data = []

  for i in range(1, len(values)):
    if values[i] in list_invitee:
      final_emails.append(list_emails[i])
      final_data.append({'FIO': list_fio[i], 'github': values[i], 'email': list_emails[i]})

  final_emails = ','.join(final_emails)

  script = google_api.googleapiclient.discovery.build(
      'script', 'v1', credentials=credentials)
  
  body = {"function": "sendMailInvitation", "devMode": True,
          "parameters": [final_emails, repo_name]}
  
  response = script.scripts().run(body=body, scriptId=SCRIPT_ID).execute()
  return final_data