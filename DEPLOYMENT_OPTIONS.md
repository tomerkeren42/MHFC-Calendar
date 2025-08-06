# Deployment Options for Maccabi Haifa Calendar Sync

This guide covers different ways to run the automated sync, from local Mac to cloud servers.

## 🖥️ Option 1: Local Mac (Current Setup)

### Requirements
- ✅ **Your Mac must be running** for the sync to work
- ✅ **No manual triggering** needed once set up
- ✅ **Cron triggers** the job automatically
- ✅ **Customizable frequency**

### Setup Commands

**Daily sync (recommended):**
```bash
./sync_maccabi.sh setup daily        # 9:00 AM every day
```

**Other frequencies:**
```bash
./sync_maccabi.sh setup hourly       # Every hour
./sync_maccabi.sh setup twice-daily  # 9:00 AM and 9:00 PM
./sync_maccabi.sh setup weekly       # Mondays at 9:00 AM
```

### Pros & Cons
✅ **Pros**: Simple setup, no additional costs, full control
❌ **Cons**: Mac must stay on, stops when Mac sleeps/shuts down

---

## ☁️ Option 2: Cloud Server (Always Running)

### 2A. GitHub Actions (Free, Recommended)

**Pros**: Free, no server maintenance, always running
**Cons**: Requires some GitHub setup

**Setup Steps:**
1. Push your code to a GitHub repository
2. Add `credentials.json` as a GitHub Secret
3. Create GitHub Actions workflow

**Example workflow file** (`.github/workflows/sync.yml`):
```yaml
name: Maccabi Haifa Calendar Sync
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9:00 AM UTC
  workflow_dispatch:     # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-api-python-client pytz
    - name: Setup credentials
      run: echo '${{ secrets.GOOGLE_CREDENTIALS }}' > credentials.json
    - name: Run sync
      run: python3 auto_sync.py
```

### 2B. Raspberry Pi (Low-cost home server)

**Pros**: Always on, low power, one-time cost (~$50)
**Cons**: Initial hardware setup

**Setup Steps:**
1. Install Raspberry Pi OS
2. Copy your sync files to Pi
3. Set up cron job like on Mac
4. Runs 24/7 in your home

### 2C. Cloud VPS (DigitalOcean, AWS, etc.)

**Pros**: Professional, always on, reliable
**Cons**: Monthly cost (~$5-20/month)

**Setup Steps:**
1. Create small cloud server
2. Install Python and dependencies
3. Copy sync files and credentials
4. Set up cron job

---

## 🔋 Option 3: Mac Sleep Prevention

Keep your Mac running automatically:

### 3A. Prevent Sleep During Sync
```bash
# Add to cron job to prevent sleep
caffeinate -s ./sync_maccabi.sh cron
```

### 3B. Wake Mac for Sync (macOS)
```bash
# Schedule wake-up before sync
sudo pmset repeat wakeorpoweron MTWRFSU 08:55:00
```

### 3C. Menu Bar App (Keep Mac Awake)
- Use apps like "Amphetamine" or "Caffeine"
- Keep Mac awake during work hours

---

## 🤖 Option 4: Mobile/Always-On Solutions

### 4A. Termux (Android)
Run Python scripts on Android phone:
1. Install Termux app
2. Install Python and dependencies
3. Set up sync script
4. Use cron-like scheduling

### 4B. iSH (iOS)
Limited but possible on jailbroken iOS devices

---

## 📊 Comparison Table

| Option | Cost | Reliability | Setup Difficulty | Always On |
|--------|------|-------------|------------------|-----------|
| **Local Mac** | Free | Medium | Easy | ❌ |
| **GitHub Actions** | Free | High | Medium | ✅ |
| **Raspberry Pi** | ~$50 | High | Medium | ✅ |
| **Cloud VPS** | $5-20/mo | Very High | Hard | ✅ |
| **Mac + Wake** | Free | Medium | Medium | ⚡ |

---

## 🎯 Recommendations

### For Most Users (Daily sync is enough)
```bash
# Run on your Mac - simple and effective
./sync_maccabi.sh setup daily
```

### For Power Users (Want 24/7 reliability)
1. **Best Free Option**: GitHub Actions
2. **Best Paid Option**: Raspberry Pi (one-time cost)
3. **Enterprise Option**: Cloud VPS

### For Minimal Setup
```bash
# Just run manually when you think about it
./sync_maccabi.sh run
```

---

## 🛠️ Current Status Check

See what's currently set up:
```bash
./sync_maccabi.sh status       # Check last sync
crontab -l                     # View current cron jobs
./sync_maccabi.sh logs         # See recent activity
```

## 🗑️ Remove Automation

To stop automatic syncing:
```bash
crontab -e                     # Edit cron jobs
# Delete the line with sync_maccabi.sh

# Or remove all cron jobs:
crontab -r
```

---

Choose the option that best fits your needs and technical comfort level!