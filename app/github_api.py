from flask import render_template, flash, redirect, session, url_for, request, g, Markup
import os
from app import app
from app import google_api

# for FlaskForm
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

from flask_dance.contrib.github import make_github_blueprint, github

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_ID_GITHUB = 'b7642ad896f5597b5f6b'
CLIENT_SECRET_GITHUB = '14320921a9af8e0c15a1f2c59ea8eaae043f33e7'
SCOPES_GITHUN = 'repo'

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
      name = subject + '-' + year + '-' + group
      create_new_repo_by_template = github.post('/repos/spasartyom/Hello-World/generate', json={"name": name, "description": 'This repository is created by template'}, headers={"Accept": 'application/vnd.github.baptiste-preview+json'})
      # pprint(create_new_repo_by_template.json())
      return redirect(url_for('index'))
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