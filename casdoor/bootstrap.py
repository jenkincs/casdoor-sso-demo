"""Build initial Casdoor configuration from deployment secrets, never from Git."""
import json
import os
import pathlib
import re

def required(key):
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Missing {key}")
    if '\n' in value or '\r' in value:
        raise RuntimeError(f"Invalid multiline {key}")
    return value

def application(name, organization, client_id, secret, callback, home):
    return {
        'owner': 'admin', 'name': name, 'displayName': name.title(),
        'category': 'Default', 'type': 'All', 'organization': organization,
        'homepageUrl': home, 'cert': 'cert-built-in',
        'enablePassword': True, 'enableSignUp': False, 'enableAutoSignin': True,
        'clientId': client_id, 'clientSecret': secret, 'providers': [],
        'signinMethods': [{'name': 'Password', 'displayName': 'Password', 'rule': 'All'}],
        'signupItems': [], 'grantTypes': ['authorization_code'],
        'redirectUris': [callback] if callback else [],
        'tokenFormat': 'JWT', 'tokenFields': [], 'expireInHours': 1,
        'cookieExpireInHours': 12, 'failedSigninLimit': 5, 'failedSigninFrozenTime': 15,
    }

def build_initial_data(env):
    booking = env['BOOKING_URL'].rstrip('/')
    invoice = env['INVOICE_URL'].rstrip('/')
    org = {
        'owner': 'admin', 'name': 'sso-demo', 'displayName': 'SSO Playground',
        'passwordType': 'bcrypt', 'passwordOptions': ['AtLeast8'],
        'countryCodes': ['CN'], 'languages': ['zh', 'en'],
        'defaultApplication': 'booking', 'defaultTokenFormat': 'JWT',
        'isProfilePublic': False, 'accountItems': [], 'tags': [],
    }
    apps = [
        application('booking','sso-demo',env['BOOKING_CLIENT_ID'],env['BOOKING_CLIENT_SECRET'],booking+'/login/oauth2/code/casdoor',booking),
        application('invoice','sso-demo',env['INVOICE_CLIENT_ID'],env['INVOICE_CLIENT_SECRET'],invoice+'/callback',invoice),
        application('app-built-in','built-in',env['ADMIN_CLIENT_ID'],env['ADMIN_CLIENT_SECRET'],'',env['CASDOOR_URL']),
    ]
    user = {
        'owner':'sso-demo','name':'demo','id':'sso-demo-user-001',
        'type':'normal-user','password':env['DEMO_PASSWORD'],'displayName':'Demo Tester',
        'isAdmin':False,'isForbidden':False,'isDeleted':False,
        'signupApplication':'booking','properties':{},'groups':[],
    }
    return {'organizations':[org], 'applications':apps, 'users':[user]}

if __name__ == '__main__':
    keys = ['DATABASE_URL','CASDOOR_URL','BOOKING_URL','INVOICE_URL','BOOKING_CLIENT_ID',
            'BOOKING_CLIENT_SECRET','INVOICE_CLIENT_ID','INVOICE_CLIENT_SECRET',
            'ADMIN_CLIENT_ID','ADMIN_CLIENT_SECRET','DEMO_PASSWORD','ADMIN_PASSWORD']
    env = {key:required(key) for key in keys}
    data = pathlib.Path('/data'); data.mkdir(exist_ok=True)
    (data/'init_data.json').write_text(json.dumps(build_initial_data(env)),encoding='utf-8')
    replacements = {
        'httpport':os.environ.get('PORT','8000'), 'runmode':'prod',
        'driverName':'postgres', 'dataSourceName':env['DATABASE_URL'], 'dbName':'',
        'origin':env['CASDOOR_URL'].rstrip('/'), 'originFrontend':env['CASDOOR_URL'].rstrip('/'),
        'initDataFile':'/data/init_data.json', 'initDataNewOnly':'false', 'initDataMerge':'true',
        'initAdminPassword':env['ADMIN_PASSWORD'], 'defaultApplication':'app-built-in',
        'socks5Proxy':'', 'enableErrorMask':'true', 'forceLanguage':'zh',
        'sessionname':'casdoor.sid', 'sessiongcmaxlifetime':'43200',
    }
    config = pathlib.Path('/conf/app.conf').read_text()
    for key,value in replacements.items():
        line = f'{key} = {value}'
        pattern = r'^'+re.escape(key)+r'\s*=.*$'
        if re.search(pattern,config,re.M):
            config = re.sub(pattern,lambda _m:line,config,flags=re.M)
        else:
            config += '\n'+line+'\n'
    conf = data/'app.conf'; conf.write_text(config,encoding='utf-8')
    for p in [conf,data/'init_data.json']: p.chmod(0o600)
    os.execv('/server',['/server','--config',str(conf)])
