import json
import pathlib
import time
import urllib.request
import urllib.error

def get(url):
    with urllib.request.urlopen(url,timeout=10) as response:
        return response.status, response.read()

targets = [('Casdoor','http://localhost:8000/api/health'),('Booking','http://localhost:8080/health'),('Invoice','http://localhost:8081/health')]
remaining = dict(targets)
for attempt in range(90):
    for name,url in list(remaining.items()):
        try:
            if get(url)[0] == 200:
                print(name+': local health check passed')
                del remaining[name]
        except (OSError,urllib.error.URLError):
            pass
    if not remaining:break
    time.sleep(2)
if remaining:
    raise SystemExit('Startup not ready: '+', '.join(remaining)+'. Run docker compose --env-file .demo/runtime.env -f compose.codespaces.yml logs --tail=80')
for port in [8080,8081]:
    try:
        get(f'http://localhost:{port}/api/business')
        raise SystemExit(f'Protected API at {port} unexpectedly allowed unauthenticated access')
    except urllib.error.HTTPError as error:
        if error.code!=401:raise
        print(f'App {port}: protected API correctly returned 401')
urls = json.loads(pathlib.Path('.demo/status.json').read_text())
for key,url in urls.items():print(key+': '+url)
print('Local checks passed. Public-port access and browser SSO must still be verified.')
