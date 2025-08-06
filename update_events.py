#!/usr/bin/env python3
"""
Script to update existing calendar events with "not final time" indicators
"""

from add_to_calendar import GoogleCalendarManager
from scaper import scrape_haifa_matches
import json


def update_events_in_calendar(calendar_id='primary'):
    """
    Update existing events in specified calendar
    
    Args:
        calendar_id: Google Calendar ID (default: 'primary')
    """
    try:
        print("🔄 Starting update process...")
        
        # Initialize calendar manager
        calendar_manager = GoogleCalendarManager()
        
        # Get fresh match data
        print("🕷️  Scraping latest match data...")
        matches_json = scrape_haifa_matches()
        matches = json.loads(matches_json)
        
        # Find matches with "not final time" indicator
        not_final_matches = [m for m in matches if m.get('not_final_time')]
        
        if not not_final_matches:
            print("💭 No matches found with 'not final time' indicator")
            return
        
        print(f"📋 Found {len(not_final_matches)} matches with 'not final time' indicator:")
        for match in not_final_matches:
            print(f"   • {match['home_team']} vs {match['away_team']} - {match['not_final_time']}")
        
        # Update events
        print(f"\n🔄 Updating existing events in calendar...")
        updated_count = calendar_manager.find_and_update_maccabi_events(calendar_id)
        
        if updated_count > 0:
            print(f"\n✅ Successfully updated {updated_count} events!")
        else:
            print("\n💭 No events needed updating")
            print("   Possible reasons:")
            print("   - Events already have 'not final' indicators")
            print("   - No matching events found in calendar")
            print("   - Matches don't actually have 'not final' indicators on website")
        
    except Exception as e:
        print(f"❌ Error during update: {e}")


def update_maccabi_calendar():
    """
    Specifically update the מכבי calendar
    """
    # מכבי calendar ID from previous output
    maccabi_calendar_id = "3cna52k26be1inadhid6s0i360@group.calendar.google.com"
    
    print("🎯 Updating מכבי calendar specifically...")
    update_events_in_calendar(maccabi_calendar_id)


def show_example_usage():
    """
    Show examples of how to use the update functionality
    """
    print("📚 Update Events - Usage Examples")
    print("=" * 40)
    
    print("\n1️⃣  Update main calendar:")
    print("""
from add_to_calendar import GoogleCalendarManager

calendar_manager = GoogleCalendarManager()
updated_count = calendar_manager.find_and_update_maccabi_events('primary')
print(f"Updated {updated_count} events")
""")
    
    print("2️⃣  Update specific calendar:")
    print("""
# Replace with your calendar ID
calendar_id = "your_calendar_id@group.calendar.google.com"
updated_count = calendar_manager.find_and_update_maccabi_events(calendar_id)
""")
    
    print("3️⃣  Check which matches have 'not final' indicators:")
    print("""
from scaper import scrape_haifa_matches
import json

matches = json.loads(scrape_haifa_matches())
not_final_matches = [m for m in matches if m.get('not_final_time')]

for match in not_final_matches:
    print(f"{match['home_team']} vs {match['away_team']} - {match['not_final_time']}")
""")


if __name__ == "__main__":
    print("🔄 Maccabi Haifa Event Updater")
    print("=" * 35)
    
    choice = input("""
Choose an option:
1. Update events in main calendar
2. Update events in מכבי calendar
3. Update events in custom calendar
4. Show usage examples
5. Exit

Enter your choice (1-5): """)
    
    if choice == "1":
        update_events_in_calendar('primary')
    elif choice == "2":
        update_maccabi_calendar()
    elif choice == "3":
        calendar_id = input("Enter calendar ID: ").strip()
        if calendar_id:
            update_events_in_calendar(calendar_id)
        else:
            print("❌ No calendar ID provided")
    elif choice == "4":
        show_example_usage()
    elif choice == "5":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")