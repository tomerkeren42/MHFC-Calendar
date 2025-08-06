#!/usr/bin/env python3
"""
Example script showing how to integrate the Maccabi Haifa scraper 
with Google Calendar functionality
"""

import json
from scaper import scrape_haifa_matches
from add_to_calendar import GoogleCalendarManager, add_match_to_calendar


def add_all_matches_to_calendar():
    """
    Scrape all Maccabi Haifa matches and add them to Google Calendar
    """
    print("Scraping Maccabi Haifa matches...")
    
    # Get matches data from scraper
    matches_json = scrape_haifa_matches()
    matches = json.loads(matches_json)
    
    print(f"Found {len(matches)} matches")
    
    # Initialize calendar manager
    try:
        calendar_manager = GoogleCalendarManager()
        
        # Add each match to calendar
        added_count = 0
        for i, match in enumerate(matches, 1):
            print(f"Adding match {i}/{len(matches)}: {match.get('home_team', '')} vs {match.get('away_team', '')}")
            
            event_id = calendar_manager.add_event_from_json(match)
            if event_id:
                added_count += 1
                print(f"✅ Added successfully (ID: {event_id})")
            else:
                print("❌ Failed to add")
        
        print(f"\n🎉 Successfully added {added_count}/{len(matches)} matches to Google Calendar!")
        
    except Exception as e:
        print(f"Error setting up calendar manager: {e}")
        print("\nMake sure you have:")
        print("1. Created a Google Cloud Project")
        print("2. Enabled the Google Calendar API")
        print("3. Downloaded credentials.json file")
        print("4. Placed credentials.json in the same directory as this script")


def add_single_match_example():
    """
    Example of adding a single match to calendar
    """
    # Example match data (from your scraper format)
    sample_match = {
        "date_day": "7",
        "date_month": "אוג'",
        "time": "22:00",
        "competition": "קונפרנס ליג",
        "venue": "זונדקריפטו ארנה",
        "home_team": "מכבי",
        "away_team": "ראקוב צ'נסטוחובה"
    }
    
    print("Adding sample match to calendar...")
    event_id = add_match_to_calendar(sample_match)
    
    if event_id:
        print(f"✅ Match added successfully! Event ID: {event_id}")
    else:
        print("❌ Failed to add match")


if __name__ == "__main__":
    print("Maccabi Haifa Calendar Integration")
    print("=" * 40)
    
    choice = input("""
Choose an option:
1. Add all scraped matches to calendar
2. Add sample match to calendar
3. Exit

Enter your choice (1-3): """)
    
    if choice == "1":
        add_all_matches_to_calendar()
    elif choice == "2":
        add_single_match_example()
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice")