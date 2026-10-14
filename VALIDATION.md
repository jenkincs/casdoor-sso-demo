# Validation status

Validated on 2026-10-14:

- Vue/Vite production build: passed.
- Invoice Node test: passed (unauthenticated business API 401, invalid logout CSRF 403, valid logout redirects and clears session).
- Booking Spring Boot 3.5.16 tests: 2 passed (unauthenticated business API 401, authenticated simulated OIDC user can access data, logout requires CSRF).
- Casdoor bootstrap test: passed (separate client identities, exact callback URLs, no admin rights for the demo user, sign-up disabled).
- render.yaml against Render's current official JSON Schema: passed.

Created Neon project `casdoor-sso-demo`, id `bitter-smoke-71658602`, PostgreSQL 17 in Singapore, in the connected Free-plan organization. Existing project Test was left unchanged.

Not yet validated:

- Docker image builds on Render and all three public service health checks.
- Casdoor startup against Neon, generated signing certificate and real account login.
- Real OIDC signature/issuer/audience/state/nonce/PKCE interoperability.
- Cross-domain A → B → A automatic sign-in, reload and local logout in real browsers.

Deployment status:

- GitHub write permission was verified by a successful file commit on 2026-10-14 after reconnecting.
- Render workspace Jenkin Tang's Workspace (tea-csppthl6l47c738gmkpg) was confirmed by the user.
- Public deployment and real-browser SSO verification remain in progress.

No credentials are included in this source package.
