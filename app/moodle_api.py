from flask import render_template, flash, redirect, session, url_for, request, g, Markup, json
import os
import flask
import requests
from app import app
from app import google_api

@app.route('/moodle')
def render_moodle():
  endpoint = 'https://test-bsc.moodlecloud.com/webservice/rest/server.php?wstoken=6fc59f99230d7bb8376afa8690369b7f&wsfunction=core_enrol_get_users_courses&moodlewsrestformat=json&userid=3'
  response = requests.get(endpoint)
  courses = []
  for item in response.json():
    courses.append({"id": item['id'],"name" : item['fullname']})
  _items_groups = google_api.db.groups.find()
  items_groups = [item for item in _items_groups]
  return render_template('moodle.html', courses=courses, groups=items_groups)

@app.route('/moodle-add', methods=['POST'])
def add_users_moodle():
  endpoint = 'https://test-bsc.moodlecloud.com/webservice/rest/server.php?wstoken=6fc59f99230d7bb8376afa8690369b7f&wsfunction=enrol_manual_enrol_users&moodlewsrestformat=json&'
    course_id = request.form['course']
  spreadsheet_id = request.form['groups']
  data_enrolment = []
  data_enrolment = make_users_list(course_id, spreadsheet_id)
  for i in range(len(data_enrolment)):
    tmp_endpoint = 'enrolments[0][roleid]=%(roleid)s&enrolments[0][userid]=%(userid)s&enrolments[0][courseid]=%(courseid)s' % data_enrolment[i]
    final_endpoint = endpoint + tmp_endpoint
    response_add = requests.get(final_endpoint)
  
  return redirect(url_for('index'))




def make_users_list(course_id, ss_id):
  if 'credentials' not in google_api.flask.session:
      return google_api.flask.redirect('authorize')
  # Load credentials from the session.
  credentials = google_api.google.oauth2.credentials.Credentials(
      **google_api.flask.session['credentials'])

  ss = google_api.googleapiclient.discovery.build(
      'sheets', 'v4', credentials=credentials)

  # Пример чтения файла
  # поменять размерность range
  response_ss = ss.spreadsheets().values().get(
      spreadsheetId=ss_id,
      range='A1:I4',
      majorDimension='COLUMNS'
  ).execute()
  values = response_ss['values'][2]
  
  final_data = []

  for i in range(1, len(values)):
    final_data.append({'roleid': 5, 'userid': values[i], 'courseid': course_id})

  return final_data