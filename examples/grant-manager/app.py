import re
from flask import Flask, redirect, request, render_template, session, send_from_directory
from flask.ext.session import Session
from linode import LinodeClient, LinodeLoginClient
from linode import OAuthScopes, ApiError, User, OAuthToken
import config
from functools import wraps

app=Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key

def get_login_client():
    return LinodeLoginClient(config.client_id, config.client_secret, base_url=config.login_base_url)

def get_linode_client():
    # make a LinodeClient with info from the loggged in users' serssion
    return LinodeClient(request.cookies.get('token'), base_url=config.api_base_url)

def is_logged_in(f):
    @wraps(f)
    def _logged_in_or_redirect(*args, **kwargs):
        if not request.cookies.get('token'):
            return redirect('/')
        return f(*args, **kwargs)

    return _logged_in_or_redirect

@app.route('/')
def index():
    if request.cookies.get('token'):
        return redirect('/manager')

    login_client = get_login_client()
    return render_template('index.html', login_url=login_client.generate_login_url(scopes=[OAuthScopes.Users.all, OAuthScopes.Tokens.delete]))

@app.route('/auth_callback')
def auth_callback():
    code = request.args.get('code')
    login_client = get_login_client()
    token, scopes = login_client.finish_oauth(code)

    # ensure we have sufficient scopes
    if not OAuthScopes.Users.delete in scopes:
        return render_template('error.html', error='Insufficient scopes granted to manage users!')

    resp = redirect('/manager')
    resp.set_cookie('token', token)
    return resp

@app.route('/manager')
@is_logged_in
def manager():
    client = get_linode_client()
    users = client.account.get_users()

    restricted_users = [ u for u in users if u.restricted ]
    unrestricted_users = [ u for u in users if not u.restricted ]

    if len(restricted_users) < 1:
        return render_template('no_grants.html')

    linode_grants = { l.id: [] for l in restricted_users[0].grants.linode }
    for u in restricted_users:
        for g in u.grants.linode:
            linode_grants[g.id].append((u, g))

    dnszone_grants = { l.id: [] for l in restricted_users[0].grants.dnszone }
    for u in restricted_users:
        for g in u.grants.dnszone:
            dnszone_grants[g.id].append((u, g))

    stackscript_grants = { l.id: [] for l in restricted_users[0].grants.stackscript }
    for u in restricted_users:
        for g in u.grants.stackscript:
            stackscript_grants[g.id].append((u, g))

    #nodebalancer_grants = { l.id: [] for l in restricted_users[0].grants.nodebalancer }
    #for u in restricted_users:
    #    for g in u.grants.nodebalancer:
    #        nodebalancer_grants[g.id].append((u, g))

    return render_template('grants.html', restricted_users=restricted_users, unrestricted_users=unrestricted_users,
            linode_grants=linode_grants, dnszone_grants=dnszone_grants,
            stackscript_grants=stackscript_grants)#, nodebalancer_grants=nodebalancer_grants)

@app.route('/users/<username>', methods=['GET'])
@is_logged_in
def user_display(username=None):
    client = get_linode_client()

    # test that user is valid
    try:
        user = User(client, username)
        user.email
    except ApiError:
        return render_template('error.html', error='Invalid user.')

    return render_template('user.html', user=user)

@app.route('/logout')
@is_logged_in
def logout():
    #client = get_linode_client()
    #cur_token = OAuthToken(client, request.cookies.get('token'))
    #cur_token.delete()

    ret = redirect('/')
    ret.set_cookie('token','',expires=0)
    return ret

if __name__ == '__main__':
    app.debug=True
    app.run()
