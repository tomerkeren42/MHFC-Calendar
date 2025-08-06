# Google Calendar Integration Setup

To use the calendar functionality, you need to set up Google Calendar API credentials.

## Setup Steps

### 1. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Make sure billing is enabled (free tier is sufficient)

### 2. Enable Google Calendar API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### 3. Configure OAuth Consent Screen (IMPORTANT!)
1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" (unless you have Google Workspace)
3. Fill in the required fields:
   - App name: "Maccabi Haifa Calendar" 
   - User support email: your email (tomerkeren42@gmail.com)
   - Developer contact email: your email
4. Click "Save and Continue"
5. Skip "Scopes" section (click "Save and Continue")
6. **Add Test Users**: Click "Add Users" and add your email (tomerkeren42@gmail.com)
7. Click "Save and Continue"

### 4. Create Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Maccabi Haifa Calendar")
5. Download the JSON file
6. Rename it to `credentials.json` and place it in your project directory

### 5. First Run Authentication
When you first run the script:
1. It will open a browser window
2. Sign in to your Google account
3. Grant permission to access your calendar
4. The script will save a `token.json` file for future use

## Usage Examples

### Add a Single Match
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
```

### Add All Scraped Matches
```python
from scaper import scrape_haifa_matches
from add_to_calendar import GoogleCalendarManager
import json

# Get matches
matches_json = scrape_haifa_matches()
matches = json.loads(matches_json)

# Add to calendar
calendar_manager = GoogleCalendarManager()
for match in matches:
    calendar_manager.add_event_from_json(match)  # Uses main calendar
```

### Using Different Calendars

#### List Available Calendars
```python
calendar_manager = GoogleCalendarManager()
calendars = calendar_manager.list_calendars()
# This will print all your calendars with their IDs
```

#### Add to Specific Calendar
```python
# Add to specific calendar by ID
calendar_id = "your_calendar_id_here"
calendar_manager.add_event_from_json(match_data, calendar_id)

# Or use the interactive utility
python calendar_utils.py
```

#### Create Dedicated Maccabi Calendar
```python
# The utility script can create a dedicated calendar
python calendar_utils.py
# Choose option 3 to create "Maccabi Haifa Matches" calendar
```

### Using the Example Script
```bash
python example_calendar_integration.py
```

## File Structure
After setup, your directory should contain:
- `scaper.py` - Your web scraper
- `add_to_calendar.py` - Calendar integration
- `credentials.json` - Google API credentials (you download this)
- `token.json` - OAuth token (auto-generated after first auth)
- `example_calendar_integration.py` - Example usage

## Event Details
Each calendar event includes:
- **Title**: "Home Team vs Away Team - Competition"
- **Date & Time**: Converted to Israel timezone
- **Duration**: 2 hours (configurable)
- **Location**: Stadium/venue name
- **Reminders**: 1 day before (email) + 1 hour before (popup)

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the credentials file from Google Cloud Console
- Rename it to exactly `credentials.json`
- Place it in the same directory as your Python scripts

### "Access blocked: Calendar has not completed the Google verification process" (Error 403)
This is the most common error when setting up a new app. Fix it by:

1. **Configure OAuth Consent Screen properly**:
   - Go to Google Cloud Console > "APIs & Services" > "OAuth consent screen"
   - Make sure you've added your email as a test user
   - Your email must EXACTLY match the one you're signing in with

2. **Add yourself as a test user**:
   - In OAuth consent screen, go to "Test users"
   - Click "Add Users" and add: tomerkeren42@gmail.com
   - Save the changes

3. **Alternative - Set to Internal** (if you have Google Workspace):
   - Change user type from "External" to "Internal"
   - This allows all users in your organization to use the app

4. **Clear browser cache and try again**:
   - Delete `token.json` if it exists
   - Clear your browser cache
   - Run the script again

### "Access denied" or other permission errors
- Make sure you've enabled the Google Calendar API in your Google Cloud project
- Check that your OAuth consent screen is configured
- Try deleting `token.json` and re-authenticating

### "Invalid date" errors
- The script expects Hebrew month names as used by the Maccabi Haifa website
- Supported months: ינו', פבר', מרץ', אפר', מאי', יונ', יול', אוג', ספט', אוק', נוב', דצמ'

## Security Notes
- Keep `credentials.json` secure and don't commit it to public repositories
- The `token.json` file contains your access tokens - also keep it secure
- Consider adding both files to your `.gitignore`