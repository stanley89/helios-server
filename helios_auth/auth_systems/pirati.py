# -*- coding: utf-8 -*-
"""
Pirati Authentication

"""

from django.http import *
from django.core.mail import send_mail
from django.conf import settings

import urllib2

from requests_oauthlib import OAuth2Session

import json


# some parameters to indicate that status updating is not possible
STATUS_UPDATES = False

# display tweaks
LOGIN_MESSAGE = "Přihlásit se pirátskou identitou"
PIRATI_ENDPOINT_URL = 'https://auth2.pirati.cz/auth/realms/pirati/protocol/openid-connect/auth'
PIRATI_TOKEN_URL = 'https://auth2.pirati.cz/auth/realms/pirati/protocol/openid-connect/token'
PIRATI_USERINFO_URL = 'https://auth2.pirati.cz/auth/realms/pirati/protocol/openid-connect/userinfo'

def get_auth_url(request, redirect_url):
  oauth = OAuth2Session(settings.PIRATI_CLIENT_ID, redirect_uri=redirect_url)
  url, state = oauth.authorization_url(PIRATI_ENDPOINT_URL)
  request.session['redirect_url'] = redirect_url
  return url

def get_user_info_after_auth(request):
  oauth = OAuth2Session(settings.PIRATI_CLIENT_ID, redirect_uri=request.session['redirect_url'])
  token = oauth.fetch_token(PIRATI_TOKEN_URL, client_secret=settings.PIRATI_CLIENT_SECRET,code=request.GET['code'])
  response = oauth.get(PIRATI_USERINFO_URL)
  data = response.json()
  print data
  return {'type' : 'pirati', 'user_id': data['preferred_username'], 'name': data['name'], 'info': {'email': data['email']}, 'token':{}}
    
def do_logout(user):
  """
  logout of Pirate
  """
  return None
  
def update_status(token, message):
  """
  simple update
  """
  pass

def send_message(user_id, user_name, user_info, subject, body):
  """
  send email to pirate user, user_id is combined with the domain to get the email.
  """
  send_mail(subject, body, settings.SERVER_EMAIL, ["%s <%s@pirati.cz>" % (user_name, user_id)], fail_silently=False)
  
def generate_constraint(category_id, user):
  return category_id

def eligibility_category_id(constraint):
  return constraint

def check_constraint(constraint, user):
  """
  for eligibility
  """
  userinfo = json.load(urllib2.urlopen("https://graph.pirati.cz/user/" + user.user_id))
  id = userinfo[u'id']
  usergroups = json.load(urllib2.urlopen("https://graph.pirati.cz/" + id + "/groups"))
  for usergroup in usergroups:
    if usergroup[u'id'] == constraint:
      return True
  return False

def can_list_categories():
  """
  yep, we can
  """
  return True

def list_categories(user):
  """
  list groups from the graph api
  """
  groups = json.load(urllib2.urlopen("https://graph.pirati.cz/groups"))
  groups.sort(key=lambda k: k['username'].lower())
  return [{'id': group[u'id'], 'name':group[u'username']} for group in groups]

def can_list_category_members():
  return True

def list_category_members(category_id):
  members = json.load(urllib2.urlopen("https://graph.pirati.cz/" + category_id + "/members"))
  users = []
  for member in members:
    user = json.load(urllib2.urlopen("https://graph.pirati.cz/" + member[u'id']))
    users.append({'type': 'pirati', 'id': user[u'username_clean'], 'name': user[u'username'], 'info': {'email': user[u'email']}, 'token': {}})

  return users

def pretty_eligibility(constraint):
  group = json.load(urllib2.urlopen("https://graph.pirati.cz/" + constraint))
  return "Pirate users in \"%s\" group" % group[u'username']

#
# Election Creation
#

def can_create_election(user_id, user_info):
  return True

