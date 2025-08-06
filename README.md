# Maccabi Haifa Match Scraper & Calendar Integration 🏆⚽

A Python tool that scrapes Maccabi Haifa FC match schedules and automatically adds them to your Google Calendar with correct Israel timezone.

## 🚀 Features

- **Web Scraping**: Extracts match data from official Maccabi Haifa website
- **Timezone Correction**: Converts UTC to Israel time (handles daylight saving automatically)
- **Google Calendar Integration**: Adds matches to any of your Google calendars
- **Smart Formatting**: Creates meaningful event titles, locations, and reminders
- **Hebrew Support**: Handles Hebrew month names and team names
- **"Not Final Time" Detection**: Automatically detects and includes "(לא סופי)" indicators
- **Event Updates**: Can update existing calendar events with new information
- **Interactive Tools**: Easy-to-use utilities for calendar management

## 📁 Project Structure

```
mhfc_crawler/
├── scaper.py                      # Main web scraper
├── add_to_calendar.py            # Google Calendar integration
├── calendar_utils.py             # Interactive calendar management
├── example_calendar_integration.py # Usage examples
├── update_events.py             # Update existing calendar events
├── auto_sync.py                 # Automated sync engine
├── sync_maccabi.sh              # Main automation script
├── setup_sync.py                # One-time setup for automation
├── fix_auth.py                   # Authentication troubleshooting
├── CALENDAR_SETUP.md            # Detailed Google API setup
└── README.md                    # This file
```

## 🛠️ Installation

### 1. Clone and Install Dependencies
```bash
git clone <your-repo>
cd mhfc_crawler
pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-api-python-client pytz
```

### 2. Set Up Google Calendar API
Follow the detailed guide in [`CALENDAR_SETUP.md`](CALENDAR_SETUP.md) or:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable Google Calendar API
3. Create OAuth credentials for desktop application
4. Download `credentials.json` to project directory
5. Add your email as a test user in OAuth consent screen

## 📖 Usage

### 🕷️ Basic Scraping

**Scrape all Maccabi Haifa matches:**
```python
from scaper import scrape_haifa_matches
import json

# Get all matches as JSON
matches_json = scrape_haifa_matches()
matches = json.loads(matches_json)

print(f"Found {len(matches)} matches")
for match in matches:
    print(f"{match['date_day']}/{match['date_month']} {match['time']} - {match['home_team']} vs {match['away_team']}")
```

**Sample output:**
```json
{
  "date_day": "7",
  "date_month": "אוג'",
  "time": "22:00",
  "competition": "ליגה",
  "venue": "זונדקריפטו ארנה",
  "home_team": "מכבי",
  "away_team": "ראקוב צ'נסטוחובה",
  "not_final_time": "(לא סופי)"
}
```

### 📅 Calendar Integration

**Add single match to calendar:**
```python
from add_to_calendar import add_match_to_calendar

match_data = {
    "date_day": "7",
    "date_month": "אוג'",
    "time": "22:00",
    "competition": "ליגה",
    "venue": "זונדקריפטו ארנה",
    "home_team": "מכבי",
    "away_team": "ראקוב צ'נסטוחובה"
}

event_id = add_match_to_calendar(match_data)
if event_id:
    print(f"✅ Match added! Event ID: {event_id}")
```

**Add all matches to your main calendar:**
```python
from scaper import scrape_haifa_matches
from add_to_calendar import GoogleCalendarManager
import json

# Scrape matches
matches = json.loads(scrape_haifa_matches())

# Add to calendar
calendar_manager = GoogleCalendarManager()
for match in matches:
    event_id = calendar_manager.add_event_from_json(match)
    if event_id:
        print(f"✅ Added: {match['home_team']} vs {match['away_team']}")
```

**Add to specific calendar:**
```python
# Add to specific calendar by ID
calendar_id = "your_calendar_id@group.calendar.google.com"
for match in matches:
    calendar_manager.add_event_from_json(match, calendar_id)
```

### 🔄 Update Existing Events

**Update existing events with "not final time" indicators:**
```bash
python update_events.py
```

**Programmatically update events:**
```python
from add_to_calendar import GoogleCalendarManager

calendar_manager = GoogleCalendarManager()

# Update events in main calendar
updated_count = calendar_manager.find_and_update_maccabi_events('primary')

# Update events in specific calendar
calendar_id = "your_calendar_id@group.calendar.google.com"
updated_count = calendar_manager.find_and_update_maccabi_events(calendar_id)

print(f"Updated {updated_count} events")
```

## 🤖 Automated Sync (Recommended)

**Set up automated monitoring and syncing:**

### 🚀 Quick Setup
```bash
# 1. One-time setup
python3 setup_sync.py

# 2. Test manual sync
./sync_maccabi.sh run

# 3. Setup automatic daily sync (recommended)
./sync_maccabi.sh setup daily
```

### 📋 Automation Features
- **Smart Change Detection**: Only updates when matches actually change
- **Complete Calendar Sync**: Replaces all events to ensure accuracy
- **Automatic "Not Final" Updates**: Handles time status changes
- **Robust Error Handling**: Logs issues and continues running
- **Multiple Run Modes**: One-time, cron, or continuous daemon

### 🔧 Automation Commands

**Run sync once:**
```bash
./sync_maccabi.sh run
```

**Setup automatic sync (multiple options):**
```bash
./sync_maccabi.sh setup daily        # Once per day at 9:00 AM (recommended)
./sync_maccabi.sh setup hourly       # Every hour
./sync_maccabi.sh setup twice-daily  # 9:00 AM and 9:00 PM
./sync_maccabi.sh setup weekly       # Weekly on Mondays
```

**Run in cron mode (silent):**
```bash
./sync_maccabi.sh cron   # For cron jobs
```

**Run continuously:**
```bash
./sync_maccabi.sh daemon # Syncs every 30 minutes
```

**Check status:**
```bash
./sync_maccabi.sh status # Shows last sync info
./sync_maccabi.sh logs   # Shows recent activity
```

### 📊 How It Works
1. **Monitors Website**: Scrapes latest match data
2. **Detects Changes**: Compares with previous sync using data hash
3. **Updates Calendar**: Removes old events, adds current matches
4. **Logs Activity**: Tracks all changes and errors
5. **Maintains State**: Remembers last sync to avoid unnecessary updates

### ⚙️ Customization
Edit `auto_sync.py` to change:
- **Calendar ID**: Change `MACCABI_CALENDAR_ID` variable
- **Sync Frequency**: Modify sleep time in daemon mode
- **Log Level**: Adjust logging verbosity

### 🛠️ Interactive Tools

**Use the interactive calendar manager:**
```bash
python calendar_utils.py
```

Options available:
1. **List all calendars** - See all your Google calendars and their IDs
2. **Add matches to specific calendar** - Choose which calendar to use
3. **Create dedicated Maccabi calendar** - Create and populate new calendar
4. **Update existing events** - Add "not final time" indicators to existing events
5. **Show code examples** - View usage examples

**Run the example integration:**
```bash
python example_calendar_integration.py
```

### 🔧 Advanced Usage

**List your available calendars:**
```python
from add_to_calendar import GoogleCalendarManager

calendar_manager = GoogleCalendarManager()
calendars = calendar_manager.list_calendars()

for cal in calendars:
    print(f"📅 {cal['name']}")
    print(f"   ID: {cal['id']}")
    if cal['primary']:
        print("   (Main Calendar)")
```

**Find and use specific calendar:**
```python
# Find calendar by name
target_calendar_id = None
for cal in calendars:
    if 'מכבי' in cal['name'] or 'Maccabi' in cal['name']:
        target_calendar_id = cal['id']
        break

# Add matches to found calendar
if target_calendar_id:
    for match in matches:
        calendar_manager.add_event_from_json(match, target_calendar_id)
```

**Batch add with progress tracking:**
```python
matches = json.loads(scrape_haifa_matches())
calendar_manager = GoogleCalendarManager()

added_count = 0
for i, match in enumerate(matches, 1):
    print(f"Adding match {i}/{len(matches)}: {match['home_team']} vs {match['away_team']}")
    
    event_id = calendar_manager.add_event_from_json(match)
    if event_id:
        added_count += 1
        print(f"  ✅ Success")
    else:
        print(f"  ❌ Failed")

print(f"\n🎉 Added {added_count}/{len(matches)} matches!")
```

## 🎯 Event Details

Each calendar event includes:
- **Title**: "(לא סופי) מכבי vs ראקוב צ'נסטוחובה - ליגה" (includes "not final" indicator when applicable)
- **Date & Time**: Correctly converted to Israel timezone (UTC+2/+3)
- **Duration**: 2 hours
- **Location**: Stadium/venue name
- **Reminders**: 
  - Email reminder 1 day before
  - Popup reminder 1 hour before

## 🚨 Troubleshooting

### Authentication Issues
```bash
# Fix common auth problems
python fix_auth.py
```

### "Access blocked" Error
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials/consent)
2. Add your email as a test user in OAuth consent screen
3. Delete `token.json` and try again

### "credentials.json not found"
1. Download credentials from Google Cloud Console
2. Rename to exactly `credentials.json`
3. Place in project directory

### Wrong timezone/hours
The scraper automatically converts UTC to Israel time. If you see wrong times:
- Check that your system timezone is correct
- Verify the source website shows the expected time

## 🔧 Configuration

**Change event duration:**
```python
# In add_to_calendar.py, modify this line:
end_datetime = event_datetime + timedelta(hours=3)  # Change from 2 to 3 hours
```

**Customize reminders:**
```python
# In add_to_calendar.py, modify the reminders section:
'reminders': {
    'useDefault': False,
    'overrides': [
        {'method': 'email', 'minutes': 48 * 60},  # 2 days before
        {'method': 'popup', 'minutes': 30},       # 30 minutes before
    ],
},
```

**Change team name formatting:**
```python
# In scaper.py, modify these lines:
if away_team == "מכבי חיפה":
    away_team = "מכבי"  # Change to your preferred format
```

## 📚 Examples

### 🚀 Quick Start (Automated)
```bash
# 1. Set up Google Calendar API (see CALENDAR_SETUP.md)
# 2. Download credentials.json
# 3. Set up automation
python3 setup_sync.py
./sync_maccabi.sh setup daily
```

### 📱 Quick Start (Manual)
```bash
# 1. Set up Google Calendar API (see CALENDAR_SETUP.md)
# 2. Download credentials.json
# 3. Run interactive tool
python calendar_utils.py
```

### One-liner to add all matches
```python
exec(open('example_calendar_integration.py').read())  # Run example script
```

### Custom workflow
```python
from scaper import scrape_haifa_matches
from add_to_calendar import GoogleCalendarManager
import json

def add_matches_to_maccabi_calendar():
    matches = json.loads(scrape_haifa_matches())
    calendar_manager = GoogleCalendarManager()
    
    # Find Maccabi calendar
    calendars = calendar_manager.list_calendars()
    maccabi_cal = next((cal for cal in calendars if 'מכבי' in cal['name']), None)
    
    if maccabi_cal:
        calendar_id = maccabi_cal['id']
        print(f"Adding {len(matches)} matches to {maccabi_cal['name']}")
        
        for match in matches:
            calendar_manager.add_event_from_json(match, calendar_id)
        
        print("✅ Done!")
    else:
        print("❌ Maccabi calendar not found")

# Run it
add_matches_to_maccabi_calendar()
```

## ❓ Frequently Asked Questions

### **Q: Does my Mac need to be running for the automation to work?**
**A:** Yes, for the current local setup. The cron job runs on your Mac, so it needs to be on and awake.

**Alternative solutions:**
- Use `caffeinate` to prevent sleep during sync
- Set up cloud deployment (see `DEPLOYMENT_OPTIONS.md`)
- Use "Amphetamine" app to keep Mac awake

### **Q: Do I need to manually trigger the sync?**
**A:** No! Once set up with `./sync_maccabi.sh setup daily`, it runs automatically.

### **Q: What triggers the sync job?**
**A:** Your Mac's built-in `cron` scheduler triggers it based on the schedule you choose.

### **Q: How often does it run?**
**A:** You choose the frequency:
- `daily` - Once per day at 9:00 AM (recommended)
- `hourly` - Every hour
- `twice-daily` - 9:00 AM and 9:00 PM  
- `weekly` - Monday mornings

### **Q: Can I make it run once a day?**
**A:** Yes! Use: `./sync_maccabi.sh setup daily`

### **Q: What happens if my Mac is asleep?**
**A:** The sync won't run. Options:
- Keep Mac awake during sync hours
- Use cloud deployment for 24/7 operation
- Set Mac to wake up before sync time

### **Q: How do I check if it's working?**
**A:** Run: `./sync_maccabi.sh status` to see last sync info and `./sync_maccabi.sh logs` for recent activity.

### **Q: How do I stop the automation?**
**A:** Run: `crontab -e` and delete the line with `sync_maccabi.sh`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with your Google Calendar
5. Submit a pull request

## 📜 License

This project is for personal use. Respect the Maccabi Haifa website's terms of service.

## 🏆 Enjoy Your Automated Maccabi Haifa Schedule!

Never miss a match again! 🎉⚽