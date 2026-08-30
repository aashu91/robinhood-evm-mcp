#!/usr/bin/env python3
"""Generate Telegram Mini-App HTML for Robinhood MCP."""
import os

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Robin MCP</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root {
  --bg: #0f172a;
  --card: #1e293b;
  --accent: #10b981;
  --text: #f1f5f9;
  --muted: #94a3b8;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; padding:16px; }
h1 { font-size:20px; margin-bottom:16px; color:var(--accent); }
.card { background:var(--card); border-radius:12px; padding:16px; margin-bottom:12px; }
.btn { width:100%; padding:14px; border:none; border-radius:10px; background:var(--accent); color:#fff; font-weight:600; font-size:15px; cursor:pointer; margin-top:8px; }
.btn:active { opacity:0.8; }
input { width:100%; padding:12px; border-radius:8px; border:1px solid #334155; background:#0f172a; color:#fff; margin-bottom:8px; font-size:14px; }
.status { font-size:13px; color:var(--muted); margin-top:8px; min-height:20px; }
</style>
</head>
<body>
<h1>🚀 Robin MCP Launchpad</h1>
<div class="card">
  <input id="symbol" placeholder="Token Symbol (e.g. ROBIN)">
  <input id="name" placeholder="Token Name (e.g. Robinhood MCP)">
  <button class="btn" onclick="launchToken()">Launch Token</button>
  <div class="status" id="launchStatus"></div>
</div>
<div class="card">
  <button class="btn" style="background:#6366f1" onclick="fetchTrust()">View Trust Stats</button>
  <div class="status" id="trustStatus"></div>
</div>
<div class="card">
  <button class="btn" style="background:#f59e0b" onclick="fetchReserves()">View Reserves</button>
  <div class="status" id="reservesStatus"></div>
</div>
<script>
const tg = window.Telegram.WebApp;
tg.expand();
const API = tg.initDataUnsafe?.query_id ? '/api' : 'http://localhost:8000';

async function post(method, params={}) {
  const res = await fetch(`${API}/${method}`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify(params)
  });
  return res.json();
}

async function launchToken() {
  const s = document.getElementById('symbol').value.trim();
  const n = document.getElementById('name').value.trim();
  if(!s||!n){document.getElementById('launchStatus').textContent='Fill both fields';return;}
  document.getElementById('launchStatus').textContent='Launching...';
  try {
    const r = await post('deploy_token',{symbol:s,name:n});
    document.getElementById('launchStatus').textContent='✅ '+JSON.stringify(r);
  } catch(e){document.getElementById('launchStatus').textContent='❌ '+e.message;}
}

async function fetchTrust() {
  document.getElementById('trustStatus').textContent='Loading...';
  try {
    const r = await post('get_trust_stats');
    document.getElementById('trustStatus').textContent=JSON.stringify(r,null,2);
  } catch(e){document.getElementById('trustStatus').textContent='❌ '+e.message;}
}

async function fetchReserves() {
  document.getElementById('reservesStatus').textContent='Loading...';
  try {
    const r = await post('get_reserves');
    document.getElementById('reservesStatus').textContent=JSON.stringify(r,null,2);
  } catch(e){document.getElementById('reservesStatus').textContent='❌ '+e.message;}
}
</script>
</body>
</html>"""

def generate():
    out = os.path.join(os.path.dirname(__file__), 'miniapp.html')
    with open(out, 'w') as f:
        f.write(HTML_CONTENT)
    print(f'Mini-App HTML written to {out}')
    return out

if __name__ == '__main__':
    generate()