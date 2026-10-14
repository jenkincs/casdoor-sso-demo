# No-card cloud demo

GitHub Codespaces is the no-card deployment path for this demo. Personal accounts include limited free usage. Choose a 2-core machine; do not enable paid usage. This is a temporary demo, not always-on hosting.

## Start

1. Open this repository, click **Code → Codespaces → Create codespace on main**.
2. Wait for the development container and startup script to finish. They build Casdoor, Booking and Invoice and a private PostgreSQL container automatically.
3. Open the **PORTS** tab. If the automatic public-port command was not permitted, right-click **8000**, **8080** and **8081** individually, then choose **Port Visibility → Public**. Leave **Port Protocol** at its default HTTP: the external URLs still use HTTPS; the proxy connects to the app's HTTP listener internally.
4. Open Booking's forwarded address, then log in with the ordinary test user. Username is **demo**, password is in `.demo/TEST-ACCOUNT.txt`. Only share that test account; do not share admin credentials or runtime.env.
5. Open Invoice and click login. With a working Casdoor session, it should authenticate without asking for the password again.

Public viewers do not need GitHub accounts. All three public ports are required: Casdoor must be reachable for redirects and both apps must be reachable for callbacks.

## Resume

Reopen the same stopped Codespace. The startup script will restart the containers using the same private secrets. If a build failed, open Terminal and run:

```sh
bash scripts/start-codespaces.sh
```

If three services are running but public access redirects to GitHub, make sure the three forwarded ports are Public.

## Persistence and availability

Demo PostgreSQL data is stored beneath `.demo/postgres` in the Codespace workspace. It survives normal stop/start, but deleting the Codespace deletes this demo data. The separately created Neon database remains available for a future persistent hosting deployment and is not used by this no-setup path.

Codespaces can stop after inactivity. Compute/storage quotas are finite. Stop the Codespace after testing and monitor included usage in your GitHub billing settings. Do not set paid budgets or add a payment method for this demo. If GitHub asks for paid usage after the free quota is exhausted, stop and wait for the quota to reset.

## Verification status

Configuration generation and restart behavior are tested locally. Docker builds, the real public forwarded URLs, and the complete browser SSO flow must be verified in the created Codespace before this demo is considered ready for external testers.
