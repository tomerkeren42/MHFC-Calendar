#!/usr/bin/env python3
"""
Automated Maccabi Haifa Calendar Sync
Monitors website for changes and automatically updates calendar
"""

import json
import os
import sys
import hashlib
from datetime import datetime
from add_to_calendar import GoogleCalendarManager
from scaper import scrape_haifa_matches


# Configuration
MACCABI_CALENDAR_ID = "3cna52k26be1inadhid6s0i360@group.calendar.google.com"
STATE_FILE = "sync_state.json"
LOG_FILE = "sync.log"


def log_message(message, level="INFO"):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}"
    
    # Print to console
    print(log_entry)
    
    # Append to log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


def load_state():
    """Load previous sync state"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_message(f"Error loading state file: {e}", "WARNING")
    
    return {"last_hash": None, "last_sync": None, "event_ids": {}}


def save_state(state):
    """Save current sync state"""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_message(f"Error saving state file: {e}", "ERROR")


def calculate_matches_hash(matches):
    """Calculate hash of matches data to detect changes"""
    # Sort matches by date and time for consistent hashing
    sorted_matches = sorted(matches, key=lambda x: (x['date_month'], x['date_day'], x['time']))
    
    # Create a string representation of key fields
    match_string = ""
    for match in sorted_matches:
        match_string += f"{match['date_day']}-{match['date_month']}-{match['time']}-"
        match_string += f"{match['home_team']}-{match['away_team']}-{match['venue']}-"
        match_string += f"{match['competition']}-{match.get('not_final_time', '')}"
    
    return hashlib.md5(match_string.encode('utf-8')).hexdigest()


def get_existing_maccabi_events(calendar_manager):
    """Get existing Maccabi events from calendar"""
    try:
        events = calendar_manager.get_existing_events(MACCABI_CALENDAR_ID)
        maccabi_events = []
        
        for event in events:
            summary = event.get('summary', '')
            if ('מכבי' in summary or 
                'vs' in summary or 
                'ליגה' in summary or 
                'קונפרנס' in summary):
                maccabi_events.append(event)
        
        return maccabi_events
    except Exception as e:
        log_message(f"Error getting existing events: {e}", "ERROR")
        return []


def delete_event(calendar_manager, event_id):
    """Delete an event from calendar"""
    try:
        calendar_manager.service.events().delete(
            calendarId=MACCABI_CALENDAR_ID,
            eventId=event_id
        ).execute()
        return True
    except Exception as e:
        log_message(f"Error deleting event {event_id}: {e}", "ERROR")
        return False


def sync_calendar():
    """Main sync function"""
    log_message("Starting calendar sync...")
    
    try:
        # Load previous state
        state = load_state()
        
        # Scrape current matches
        log_message("Scraping Maccabi Haifa website...")
        matches_json = scrape_haifa_matches()
        matches = json.loads(matches_json)
        
        if not matches:
            log_message("No matches found on website", "WARNING")
            return
        
        log_message(f"Found {len(matches)} matches on website")
        
        # Calculate hash of current matches
        current_hash = calculate_matches_hash(matches)
        
        # Check if anything changed
        if current_hash == state.get("last_hash"):
            log_message("No changes detected - calendar is up to date")
            return
        
        log_message("Changes detected - updating calendar...")
        
        # Initialize calendar manager
        calendar_manager = GoogleCalendarManager()
        
        # Get existing events
        existing_events = get_existing_maccabi_events(calendar_manager)
        log_message(f"Found {len(existing_events)} existing Maccabi events in calendar")
        
        # Remove all existing Maccabi events
        deleted_count = 0
        for event in existing_events:
            if delete_event(calendar_manager, event['id']):
                deleted_count += 1
        
        log_message(f"Deleted {deleted_count} existing events")
        
        # Add all current matches
        added_count = 0
        failed_count = 0
        new_event_ids = {}
        
        for match in matches:
            try:
                event_id = calendar_manager.add_event_from_json(match, MACCABI_CALENDAR_ID)
                if event_id:
                    added_count += 1
                    match_key = f"{match['date_day']}-{match['date_month']}-{match['home_team']}-{match['away_team']}"
                    new_event_ids[match_key] = event_id
                else:
                    failed_count += 1
            except Exception as e:
                log_message(f"Error adding match {match['home_team']} vs {match['away_team']}: {e}", "ERROR")
                failed_count += 1
        
        log_message(f"Added {added_count} new events, {failed_count} failed")
        
        # Update state
        state.update({
            "last_hash": current_hash,
            "last_sync": datetime.now().isoformat(),
            "event_ids": new_event_ids,
            "last_match_count": len(matches)
        })
        save_state(state)
        
        log_message(f"Calendar sync completed successfully! Updated {added_count} matches")
        
    except Exception as e:
        log_message(f"Critical error during sync: {e}", "ERROR")
        sys.exit(1)


def check_credentials():
    """Check if credentials file exists"""
    if not os.path.exists("credentials.json"):
        log_message("ERROR: credentials.json not found", "ERROR")
        log_message("Please download credentials from Google Cloud Console", "ERROR")
        sys.exit(1)


def main():
    """Main entry point"""
    log_message("=" * 50)
    log_message("Maccabi Haifa Calendar Auto-Sync Started")
    log_message("=" * 50)
    
    # Check prerequisites
    check_credentials()
    
    try:
        sync_calendar()
    except KeyboardInterrupt:
        log_message("Sync interrupted by user", "WARNING")
        sys.exit(0)
    except Exception as e:
        log_message(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)
    
    log_message("Auto-sync completed")


if __name__ == "__main__":
    main()