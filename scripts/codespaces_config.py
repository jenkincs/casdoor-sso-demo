"""Generate private demo configuration. No credential is committed to Git."""
import json
import os
import pathlib
import re
import secrets

def create_config(name, directory):
    if not re.fullmatch(r'[a-zA-Z0-9-]+', name):
        raise ValueError('Invalid Codespace name')
    directory = pathlib.Path(directory)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / 'secrets.json'
    if path.exists():
        private = json.loads(path.read_text())
    else:
        private = {key:secrets.token_urlsafe(36) for key in [
            'POSTGRES_PASSWORD','BOOKING_CLIENT_SECRET','INVOICE_CLIENT_SECRET',
            'ADMIN_CLIENT_SECRET','ADMIN_PASSWORD','DEMO_PASSWORD','SESSION_SECRET']}
        path.write_text(json.dumps(private))
        path.chmod(0o600)
    values = dict(private)
    values.update({
        'CASDOOR_URL': f'https://{name}-8000.app.github.dev',
        'BOOKING_URL': f'https://{name}-8080.app.github.dev',
        'INVOICE_URL': f'https://{name}-8081.app.github.dev',
        'BOOKING_CLIENT_ID':'sso-booking','INVOICE_CLIENT_ID':'sso-invoice','ADMIN_CLIENT_ID':'sso-admin',
        'DATABASE_URL':f"postgresql://casdoor_owner:{private['POSTGRES_PASSWORD']}@postgres:5432/casdoor?sslmode=disable",
    })
    runtime = directory / 'runtime.env'
    runtime.write_text(''.join(f'{key}={value}\n' for key,value in values.items()))
    runtime.chmod(0o600)
    (directory/'casdoor').mkdir(exist_ok=True)
    status = directory / 'status.json'
    status.write_text(json.dumps({key:values[key] for key in ['CASDOOR_URL','BOOKING_URL','INVOICE_URL']},indent=2))
    credentials = directory / 'TEST-ACCOUNT.txt'
    credentials.write_text('Demo username: demo\nDemo password: '+private['DEMO_PASSWORD']+'\n')
    credentials.chmod(0o600)
    return values

if __name__ == '__main__':
    name = os.environ.get('CODESPACE_NAME')
    if not name:
        raise SystemExit('Please run this script inside GitHub Codespaces.')
    values = create_config(name, '.demo')
    print('Demo configuration prepared; secrets kept outside Git.')
    for key in ['CASDOOR_URL','BOOKING_URL','INVOICE_URL']:
        print(key+': '+values[key])
