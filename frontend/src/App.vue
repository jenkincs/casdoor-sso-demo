<script setup>
import { ref, computed, onMounted } from 'vue';
const config = ref(null), me = ref(null), rows = ref([]), loading = ref(true), error = ref(''), busy = ref(false);
const loginError = new URLSearchParams(window.location.search).has('error');
const booking = computed(() => config.value?.app === 'booking');
const title = computed(() => booking.value ? 'Booking' : 'Invoice');
const other = computed(() => booking.value ? 'Invoice' : 'Booking');
async function request(path) { const res = await fetch(path, { credentials: 'same-origin' }); if (!res.ok) throw new Error(res.status === 401 ? '请先登录，再加载业务数据。' : '服务暂时不可用，请稍后重试。'); return res.json(); }
async function refresh() {
  loading.value = true; error.value = '';
  try { config.value = await request('/api/config'); me.value = await request('/api/me'); if (me.value.authenticated) rows.value = await request('/api/business'); else rows.value = []; }
  catch (e) { error.value = e.message; } finally { loading.value = false; }
}
async function loadData() { busy.value = true; try { rows.value = await request('/api/business'); error.value = ''; } catch(e) { error.value = e.message; } finally { busy.value = false; } }
onMounted(refresh);
</script>

<template>
  <div class="shell" :class="{ invoice: !booking }">
    <header><a class="brand" href="/"><span class="mark">C</span><span>Casdoor<span class="brand-light"> / SSO Playground</span></span></a><span class="demo-tag">PUBLIC DEMO · 模拟数据</span></header>
    <main v-if="config">
      <section class="intro"><div class="eyebrow">TWO APPS. ONE IDENTITY.</div><h1>一次登录，<br><span>畅行两个应用。</span></h1><p>体验 Casdoor 跨域单点登录。当前应用是 {{ title }}，切换到 {{ other }}，验证你的登录身份是否延续。</p><div class="app-tabs"><span :class="{active:booking}">01 / Booking</span><span :class="{active:!booking}">02 / Invoice</span></div></section>
      <section class="workspace">
        <div class="workspace-head"><div><div class="eyebrow">{{ booking ? 'APP A · SPRING BOOT' : 'APP B · NODE.JS' }}</div><h2>{{ title }} <span>{{ booking ? '订舱中心' : '账单中心' }}</span></h2></div><span class="status" :class="{online:me?.authenticated}"><i></i>{{ me?.authenticated ? '已登录' : '未登录' }}</span></div>
        <div class="identity" v-if="me?.authenticated"><div class="avatar">{{ (me.displayName || me.username || 'U').slice(0,1).toUpperCase() }}</div><div><strong>{{ me.displayName || me.username }}</strong><p>{{ me.username }}</p><code>统一身份 · {{ me.subject }}</code></div><span class="verified">IDENTITY VERIFIED</span></div>
        <div class="identity guest" v-else><div class="avatar">↗</div><div><strong>欢迎来到 {{ title }}</strong><p>点击登录，将前往统一身份中心。</p></div></div>
        <div class="actions"><a class="button primary" :href="config.loginUrl">{{ me?.authenticated ? '通过 Casdoor 再次登录' : '使用 Casdoor 登录' }} <span>↗</span></a><a class="button secondary" :href="config.otherAppUrl">打开 {{ other }} <span>→</span></a><button class="button subtle" @click="refresh" :disabled="loading">刷新登录状态</button></div>
        <form v-if="me?.authenticated" method="post" action="/logout" class="logout"><input type="hidden" :name="me.csrfParameter || '_csrf'" :value="me.csrfToken"><button>退出当前应用</button><span>清除本应用会话；Casdoor 登录仍可能有效。</span></form>
        <p class="error" v-if="error" role="alert">{{ error }}</p><p class="error" v-if="loginError" role="alert">登录未完成，请重试；如果持续失败，请联系演示维护者。</p>
        <div class="business-heading"><h3>{{ booking ? '最近订舱' : '最近账单' }}</h3><button @click="loadData" :disabled="busy">{{ busy ? '加载中…' : '测试受保护 API ↗' }}</button></div>
        <div class="locked" v-if="!me?.authenticated"><span>⌑</span><strong>业务数据需要登录后查看</strong><p>未登录请求业务 API 将返回 401。</p></div>
        <div class="table-wrap" v-else><table><thead><tr><th>{{ booking ? '订舱号' : '账单号' }}</th><th>{{ booking ? '航线' : '金额' }}</th><th>状态</th></tr></thead><tbody><tr v-for="row in rows" :key="row.id"><td>{{ row.id }}</td><td>{{ row.detail }}</td><td><span class="row-status">{{ row.status }}</span></td></tr></tbody></table></div>
      </section>
      <section class="how"><div><span>01</span><h3>先登录一个应用</h3><p>使用专用测试账号，在 Casdoor 完成登录。</p></div><div><span>02</span><h3>切换到另一个应用</h3><p>点击“打开 {{ other }}”，在当前标签页切换。</p></div><div><span>03</span><h3>验证 SSO</h3><p>在另一个应用点击登录。已有 Casdoor 会话时，无需再次输入密码。</p></div></section>
      <details><summary>测试说明与技术细节</summary><p>两个应用独立部署，使用不同 Client ID 和各自的 HttpOnly 会话 Cookie。OIDC 授权码在后端兑换；浏览器页面不会读取 Access Token 或 Client Secret。</p><p>“退出当前应用”仅结束当前应用会话，不等于退出全部应用。使用无痕窗口可测试全新的登录流程。</p><p>免费服务休眠后首次打开可能需要等待；服务重启会清除应用的演示会话，用户资料保存在独立数据库中。</p><p>此演示只包含模拟业务数据。请使用测试账号，不要输入真实客户或业务信息。</p><p>当前应用域名：<code>{{ config.publicUrl }}</code></p></details>
    </main>
    <main v-else class="loading"><h1>SSO Playground</h1><p>{{ error || '正在连接演示服务…' }}</p><button class="button primary" @click="refresh">重新连接</button></main>
    <footer><span>Casdoor × Vue 3 × {{ booking ? 'Spring Boot' : 'Node.js' }}</span><a href="https://github.com/jenkincs/casdoor-sso-demo" target="_blank" rel="noopener noreferrer">查看源码 ↗</a></footer>
  </div>
</template>
