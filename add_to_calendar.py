import json
import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarManager:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        """
        Initialize the Google Calendar Manager
        
        Args:
            credentials_file: Path to the Google API credentials JSON file
            token_file: Path to store the OAuth token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Handle Google Calendar API authentication"""
        creds = None
        
        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("Token expired, attempting to refresh...")
                    creds.refresh(Request())
                    print("Token refreshed successfully")
                except Exception as refresh_error:
                    print(f"Token refresh failed: {refresh_error}")
                    print("Refresh token may be expired or revoked. Re-authenticating...")
                    # Delete the invalid token file and re-authenticate
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                    creds = None
            
            # If refresh failed or no refresh token, do full authentication flow
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            print("Successfully authenticated with Google Calendar")
        except HttpError as error:
            print(f'An error occurred during authentication: {error}')
            raise
    
    def list_calendars(self):
        """
        List all available calendars for the authenticated user
        
        Returns:
            List of calendar dictionaries with id, name, and description
        """
        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            print("Available calendars:")
            print("-" * 50)
            
            calendar_info = []
            for calendar in calendars:
                cal_info = {
                    'id': calendar['id'],
                    'name': calendar.get('summary', 'No name'),
                    'description': calendar.get('description', ''),
                    'primary': calendar.get('primary', False)
                }
                calendar_info.append(cal_info)
                
                primary_marker = " (PRIMARY)" if cal_info['primary'] else ""
                print(f"📅 {cal_info['name']}{primary_marker}")
                print(f"   ID: {cal_info['id']}")
                if cal_info['description']:
                    print(f"   Description: {cal_info['description']}")
                print()
            
            return calendar_info
            
        except HttpError as error:
            print(f'An error occurred while listing calendars: {error}')
            return []
    
    def add_event_from_json(self, event_json, calendar_id='primary'):
        """
        Add an event to Google Calendar from JSON data
        
        Args:
            event_json: JSON string or dict containing event data with keys:
                       - date_day: Day of the month (e.g., "7")
                       - date_month: Month name in Hebrew (e.g., "אוג'")
                       - time: Time in HH:MM format (e.g., "22:00")
                       - competition: Event name/title
                       - venue: Location (optional)
                       - home_team: Home team (optional)
                       - away_team: Away team (optional)
            calendar_id: Google Calendar ID (default: 'primary' for main calendar)
        
        Returns:
            Event ID if successful, None if failed
        """
        try:
            # Parse JSON if it's a string
            if isinstance(event_json, str):
                event_data = json.loads(event_json)
            else:
                event_data = event_json
            
            # Convert Hebrew month to number
            month_map = {
                'ינו': 1, 'פבר': 2, 'מרץ': 3, 'אפר': 4, 'מאי': 5, 'יונ': 6,
                'יול': 7, 'אוג': 8, 'ספט': 9, 'אוק': 10, 'נוב': 11, 'דצמ': 12,
                'ינו\'': 1, 'פבר\'': 2, 'מרץ\'': 3, 'אפר\'': 4, 'מאי\'': 5, 'יונ\'': 6,
                'יול\'': 7, 'אוג\'': 8, 'ספט\'': 9, 'אוק\'': 10, 'נוב\'': 11, 'דצמ\'': 12
            }
            
            # Extract data
            day = int(event_data['date_day'])
            month_hebrew = event_data['date_month']
            time_str = event_data['time']
            title = event_data.get('competition', 'Football Match')
            
            # Get month number
            month = month_map.get(month_hebrew, 1)
            
            # Determine year (assume current year or next year if month has passed)
            current_year = datetime.now().year
            current_month = datetime.now().month
            year = current_year if month >= current_month else current_year + 1
            
            # Parse time
            hour, minute = map(int, time_str.split(':'))
            
            # Create datetime
            event_datetime = datetime(year, month, day, hour, minute)
            end_datetime = event_datetime + timedelta(hours=2)  # Assume 2-hour duration
            
            # Build event title
            if 'home_team' in event_data and 'away_team' in event_data:
                # title = f"{event_data['home_team']} vs {event_data['away_team']}"
                # because team names are in hebrew, so using the english "vs" term is making the whole title in the wrong order
                title = f"{event_data['away_team']} vs {event_data['home_team']}"
                if 'competition' in event_data:
                    title += f" - {event_data['competition']}"
            
            # Add "not final time" indicator if present
            if 'not_final_time' in event_data and event_data['not_final_time']:
                title = f"{event_data['not_final_time']} {title}"
            
            # Create event
            event = {
                'summary': title,
                'location': event_data.get('venue', ''),
                'description': f"Football match: {title}",
                'start': {
                    'dateTime': event_datetime.isoformat(),
                    'timeZone': 'Asia/Jerusalem',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Asia/Jerusalem',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},       # 1 hour before
                    ],
                },
            }
            
            # Add to calendar
            event_result = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f'Event created: {event_result.get("htmlLink")}')
            print(f'Event ID: {event_result.get("id")}')
            
            return event_result.get('id')
            
        except Exception as e:
            print(f'An error occurred while adding event: {e}')
            return None
    
    def add_multiple_events(self, events_json, calendar_id='primary'):
        """
        Add multiple events from a JSON array
        
        Args:
            events_json: JSON string or list containing multiple event objects
            calendar_id: Google Calendar ID
        
        Returns:
            List of event IDs that were successfully created
        """
        try:
            if isinstance(events_json, str):
                events_data = json.loads(events_json)
            else:
                events_data = events_json
            
            created_events = []
            for event_data in events_data:
                event_id = self.add_event_from_json(event_data, calendar_id)
                if event_id:
                    created_events.append(event_id)
            
            print(f'Successfully created {len(created_events)} out of {len(events_data)} events')
            return created_events
            
        except Exception as e:
            print(f'An error occurred while adding multiple events: {e}')
            return []
    
    def get_existing_events(self, calendar_id='primary', time_min=None, time_max=None):
        """
        Get existing events from calendar
        
        Args:
            calendar_id: Google Calendar ID
            time_min: Start time filter (datetime object)
            time_max: End time filter (datetime object)
        
        Returns:
            List of events
        """
        try:
            # Default to next 12 months if no time range specified
            if not time_min:
                time_min = datetime.now()
            if not time_max:
                time_max = datetime.now() + timedelta(days=365)
            
            time_min_str = time_min.isoformat() + 'Z'
            time_max_str = time_max.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min_str,
                timeMax=time_max_str,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except HttpError as error:
            print(f'An error occurred while getting events: {error}')
            return []
    
    def update_event(self, event_id, updated_event_data, calendar_id='primary'):
        """
        Update an existing calendar event
        
        Args:
            event_id: Google Calendar event ID
            updated_event_data: New event data
            calendar_id: Google Calendar ID
        
        Returns:
            Updated event ID if successful, None if failed
        """
        try:
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=updated_event_data
            ).execute()
            
            print(f'Event updated: {updated_event.get("htmlLink")}')
            return updated_event.get('id')
            
        except HttpError as error:
            print(f'An error occurred while updating event: {error}')
            return None
    
    def find_and_update_maccabi_events(self, calendar_id='primary'):
        """
        Find existing Maccabi events and update them with "not final time" indicator if needed
        
        Args:
            calendar_id: Google Calendar ID
        
        Returns:
            Number of events updated
        """
        try:
            # Get fresh match data
            from scaper import scrape_haifa_matches
            import json
            
            matches_json = scrape_haifa_matches()
            matches = json.loads(matches_json)
            
            # Get existing events
            existing_events = self.get_existing_events(calendar_id)
            
            updated_count = 0
            
            for match in matches:
                if not match.get('not_final_time'):
                    continue  # Skip matches without "not final time" indicator
                
                # Look for matching event
                # match_title_base = f"{match['home_team']} vs {match['away_team']}"
                match_title_base = f"{match['away_team']} vs {match['home_team']}" # Writing it this way because
                #  team names are in hebrew, so using the english "vs" term is making the whole title in the wrong order
                
                for event in existing_events:
                    event_title = event.get('summary', '')
                    
                    # Check if this event matches the match and doesn't already have "not final" indicator
                    if (match_title_base in event_title and 
                        'לא סופי' not in event_title and
                        match['not_final_time']):
                        
                        # Update the event title
                        new_title = f"{match['not_final_time']} {event_title}"
                        
                        # Create updated event data
                        updated_event = {
                            'summary': new_title,
                            'location': event.get('location', ''),
                            'description': event.get('description', ''),
                            'start': event.get('start'),
                            'end': event.get('end'),
                            'reminders': event.get('reminders')
                        }
                        
                        # Update the event
                        result = self.update_event(event['id'], updated_event, calendar_id)
                        if result:
                            updated_count += 1
                            print(f"✅ Updated: {match_title_base} -> {new_title}")
                        break  # Found and updated the matching event
            
            print(f"\n🎉 Updated {updated_count} events with 'not final time' indicator!")
            return updated_count
            
        except Exception as e:
            print(f'An error occurred while updating events: {e}')
            return 0


def add_match_to_calendar(match_json, credentials_file='credentials.json'):
    """
    Convenience function to add a single match to Google Calendar
    
    Args:
        match_json: JSON data containing match information
        credentials_file: Path to Google API credentials file
    
    Returns:
        Event ID if successful, None if failed
    """
    try:
        calendar_manager = GoogleCalendarManager(credentials_file)
        return calendar_manager.add_event_from_json(match_json)
    except Exception as e:
        print(f'Failed to add match to calendar: {e}')
        return None


# Example usage
if __name__ == "__main__":
    # Example match data from your scraper
    sample_match = {
        "date_day": "7",
        "date_month": "אוג'",
        "time": "22:00",
        "competition": "קונפרנס ליג - סיבוב המוקדמות השלישי",
        "venue": "זונדקריפטו ארנה",
        "home_team": "מכבי חיפה",
        "away_team": "ראקוב צ'נסטוחובה"
    }
    
    # Add single event
    event_id = add_match_to_calendar(sample_match)
    if event_id:
        print(f"Match added to calendar with ID: {event_id}")
    else:
        print("Failed to add match to calendar")
