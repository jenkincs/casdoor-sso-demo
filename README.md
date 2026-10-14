# Casdoor SSO Playground

两个独立应用、一个 Casdoor 身份中心：Booking 使用 Vue 3 + Spring Boot，Invoice 使用 Vue 3 + Node.js。通过 OIDC Authorization Code + PKCE 实现跨域 SSO。

## 无需绑卡的试玩部署

使用 **GitHub Codespaces**：在仓库点击 **Code → Codespaces → Create codespace on main**。开发容器会自动构建和启动三个服务；将 8000、8080、8081 转发端口设为 Public 后，可通过 HTTPS 链接给外部用户测试。

详细步骤、测试账号位置和免费额度限制见 [CODESPACES.md](CODESPACES.md)。这是按需运行的临时演示，Codespace 停止后链接暂停。Docker 构建与公网 SSO 尚待创建 Codespace 后实际验证。

## 当前状态

源码已提交 GitHub，原有本地检查通过。Render 免费服务创建请求返回付款信息要求，因此不再继续 Render 部署；已增加无需绑卡的 Codespaces 配置。公网部署与真实 Casdoor 端到端登录验证尚未完成。

## 试玩流程

1. 在 Booking 点击“使用 Casdoor 登录”，用专用测试账号登录。
2. 点击“打开 Invoice”，在同一个标签页访问另一应用。
3. Invoice 还没有本地会话时点击登录；Casdoor 的已有会话应自动完成授权，无需再次输入密码。
4. 对比两个应用显示的统一身份，并测试受保护 API。
5. 在当前应用退出；当前会话被清除，Casdoor 和另一个 App 的会话不因此退出。
6. 无痕窗口应需要重新登录。直接访问任一应用也可以独立登录。

## 安全边界

- 每个 App 独立 Client ID、Client Secret 和 HttpOnly/Secure/SameSite=Lax 会话 Cookie。
- Client Secret 仅在后端使用；Access Token、Refresh Token 不返回前端、不写入跨应用链接。
- Node 使用 openid-client 验证 state、nonce、PKCE、ID Token 签名、issuer、audience 和过期时间；Spring Security 处理 OIDC，并为机密客户端启用 PKCE。
- 退出使用 POST 并校验 CSRF。未登录访问业务 API 返回 401。
- 只提供专用普通测试用户与模拟业务数据；演示关闭用户自行注册与管理应用注册。
- Casdoor 管理密码、客户端密钥、数据库连接串只存放在部署环境变量中。
- 两个 App 的本地会话是单实例内存会话，重启后需要重建；Casdoor 用户与配置持久保存在 PostgreSQL。
- 此演示尚未实现全局登出，不把本地退出称为全局退出。

## 部署

`render.yaml` 定义三个免费 Docker Web Service。Casdoor 使用 `casbin/casdoor:v4.20.0`。PostgreSQL 使用独立 Neon 项目；不要用免费服务的本地 SQLite 保存用户。

服务地址确定后必须配置精确的 HTTPS 回调地址。Casdoor 的 `BOOKING_URL`、`INVOICE_URL` 要与两个 App 的 `PUBLIC_URL` 一致。两个 App 的 `OTHER_APP_URL` 指向对方。`CASDOOR_URL` 三个服务保持一致且没有尾部斜线。

Casdoor 启动脚本根据环境变量生成初始化数据，设置独立普通用户、两个 OIDC 客户端与自动登录。内置签名证书由 Casdoor 自动生成并保存数据库。使用 Casdoor 的合并初始化模式，将声明的应用字段与数据库配置同步并关闭内置应用注册；已有用户密码由 Casdoor 保留。不要通过修改初始密码环境变量尝试重置账号。

Render 免费服务会休眠并共享运行时额度。本演示适合少量测试，不承诺全天候可用；首次访问可能需要等待服务冷启动。

## 本地构建与测试

```sh
cd frontend
npm ci
npm run build
cd ../invoice
npm ci
npm test
cd ../booking
mvn test
cd ../casdoor
python3 -m unittest test_bootstrap.py
```

本地 App 需要设置与部署相同的 URL 和客户端变量。Node 本地运行不设置 NODE_ENV=production；Spring 本地 HTTP 使用 COOKIE_SECURE=false。不要将 `.env`、初始化 JSON 或凭据提交到仓库。
