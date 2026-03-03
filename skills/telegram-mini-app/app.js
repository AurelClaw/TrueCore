// Aurel Dashboard - Telegram Mini App
const tg = window.Telegram?.WebApp;

// DOM Elements
const userEl = document.getElementById('user');
const goalsEl = document.getElementById('goals');
const skillsEl = document.getElementById('skills');
const integrationEl = document.getElementById('integration');
const sessionsEl = document.getElementById('sessions');
const outEl = document.getElementById('out');
const refreshBtn = document.getElementById('refresh');
const pingBtn = document.getElementById('ping');

// Initialize
function init() {
  if (!tg) {
    userEl.textContent = "⚠️ Nicht in Telegram WebView";
    outEl.textContent = "Bitte über Telegram Bot öffnen.";
    return;
  }

  // Tell Telegram we're ready
  tg.ready();
  tg.expand();

  // Show user info
  const user = tg.initDataUnsafe?.user;
  if (user) {
    userEl.textContent = `Hallo ${user.first_name}${user.username ? ' (@' + user.username + ')' : ''}`;
  } else {
    userEl.textContent = "Gast-Modus";
  }

  // Load initial data
  loadDashboardData();

  // Event listeners
  refreshBtn.addEventListener('click', loadDashboardData);
  pingBtn.addEventListener('click', pingBackend);
}

// Load dashboard data from backend
async function loadDashboardData() {
  outEl.textContent = "🔄 Lade Daten...";
  outEl.classList.add('loading');

  try {
    const res = await fetch('/api/dashboard', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        initData: tg.initData,
        clientTs: Date.now()
      })
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();

    // Update UI
    goalsEl.textContent = data.goals || '-';
    skillsEl.textContent = data.skills || '-';
    integrationEl.textContent = data.integration || '-';
    sessionsEl.textContent = data.sessions || '-';

    outEl.textContent = `✅ Daten geladen\n${JSON.stringify(data, null, 2)}`;

    // Haptic feedback
    tg.HapticFeedback?.impactOccurred('light');

  } catch (err) {
    outEl.textContent = `❌ Fehler: ${err.message}`;
    console.error(err);
  } finally {
    outEl.classList.remove('loading');
  }
}

// Ping backend
async function pingBackend() {
  outEl.textContent = "📡 Sende Ping...";

  try {
    const res = await fetch('/api/ping', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        initData: tg.initData,
        clientTs: Date.now()
      })
    });

    const text = await res.text();
    outEl.textContent = `${res.status === 200 ? '✅' : '❌'} ${text}`;

    if (res.ok) {
      tg.HapticFeedback?.notificationOccurred('success');
    }

  } catch (err) {
    outEl.textContent = `❌ Fehler: ${err.message}`;
  }
}

// Start
init();
