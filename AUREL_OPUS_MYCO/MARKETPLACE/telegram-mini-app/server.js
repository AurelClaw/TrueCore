// Backend for Aurel Dashboard Mini App
const express = require('express');
const crypto = require('crypto');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

const BOT_TOKEN = process.env.BOT_TOKEN;
if (!BOT_TOKEN) {
  console.error('❌ BOT_TOKEN nicht gesetzt!');
  process.exit(1);
}

// Verify Telegram initData
function verifyInitData(initData) {
  const params = new URLSearchParams(initData);
  const hash = params.get('hash');
  
  if (!hash) {
    return { ok: false, reason: 'missing hash' };
  }

  params.delete('hash');

  // Build data_check_string
  const pairs = [];
  for (const [k, v] of params.entries()) {
    pairs.push([k, v]);
  }
  pairs.sort((a, b) => a[0].localeCompare(b[0]));
  const dataCheckString = pairs.map(([k, v]) => `${k}=${v}`).join('\n');

  // secret_key = HMAC_SHA256("WebAppData", bot_token)
  const secretKey = crypto
    .createHmac('sha256', 'WebAppData')
    .update(BOT_TOKEN)
    .digest();

  // computed_hash = HMAC_SHA256(secret_key, data_check_string)
  const computed = crypto
    .createHmac('sha256', secretKey)
    .update(dataCheckString)
    .digest('hex');

  // Timing-safe comparison
  try {
    const ok = crypto.timingSafeEqual(
      Buffer.from(computed, 'hex'),
      Buffer.from(hash, 'hex')
    );
    return { ok, reason: ok ? 'ok' : 'bad signature' };
  } catch {
    return { ok: false, reason: 'hash mismatch' };
  }
}

// Check auth_date freshness
function checkFreshness(initData, maxAgeSeconds = 300) {
  const params = new URLSearchParams(initData);
  const authDate = parseInt(params.get('auth_date'), 10);
  
  if (!authDate) {
    return { ok: false, reason: 'missing auth_date' };
  }

  const now = Math.floor(Date.now() / 1000);
  const age = now - authDate;

  if (age > maxAgeSeconds) {
    return { ok: false, reason: `auth_date too old (${age}s)` };
  }

  return { ok: true };
}

// Middleware to verify initData
function authMiddleware(req, res, next) {
  const { initData } = req.body || {};

  if (!initData) {
    return res.status(401).json({ error: 'missing initData' });
  }

  // Verify signature
  const sigCheck = verifyInitData(initData);
  if (!sigCheck.ok) {
    return res.status(401).json({ error: `invalid signature: ${sigCheck.reason}` });
  }

  // Check freshness
  const freshCheck = checkFreshness(initData);
  if (!freshCheck.ok) {
    return res.status(401).json({ error: `stale: ${freshCheck.reason}` });
  }

  // Parse user data
  const params = new URLSearchParams(initData);
  const userJson = params.get('user');
  req.user = userJson ? JSON.parse(userJson) : null;

  next();
}

// Routes
app.post('/api/ping', authMiddleware, (req, res) => {
  res.json({ 
    pong: true, 
    user: req.user?.first_name || 'unknown',
    timestamp: new Date().toISOString()
  });
});

app.post('/api/dashboard', authMiddleware, (req, res) => {
  // Mock data - in production from Aurel's systems
  const data = {
    goals: 13,
    activeGoals: 1,
    completedGoals: 4,
    skills: 26,
    selfDevSkills: 11,
    integration: '9.0/10',
    sessions: 33,
    helpfulness: '96.9%',
    lastUpdate: new Date().toISOString(),
    user: req.user?.first_name
  };

  res.json(data);
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Aurel Dashboard Backend läuft auf Port ${PORT}`);
});
