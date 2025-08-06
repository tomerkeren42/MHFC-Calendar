#!/usr/bin/env python3
"""
Utility script for managing Google Calendar integration
"""

import json
from add_to_calendar import GoogleCalendarManager
from scaper import scrape_haifa_matches


def list_available_calendars():
    """
    Show all available calendars and their IDs
    """
    try:
        calendar_manager = GoogleCalendarManager()
        calendars = calendar_manager.list_calendars()
        return calendars
    except Exception as e:
        print(f"Error listing calendars: {e}")
        return []


def add_matches_to_specific_calendar():
    """
    Interactive function to add matches to a specific calendar
    """
    print("🔍 Finding your calendars...")
    calendars = list_available_calendars()
    
    if not calendars:
        print("❌ No calendars found or authentication failed")
        return
    
    print("\n📝 Select a calendar:")
    for i, cal in enumerate(calendars, 1):
        primary_text = " (Your main calendar)" if cal['primary'] else ""
        print(f"{i}. {cal['name']}{primary_text}")
    
    try:
        choice = int(input(f"\nEnter your choice (1-{len(calendars)}): ")) - 1
        if 0 <= choice < len(calendars):
            selected_calendar = calendars[choice]
            calendar_id = selected_calendar['id']
            calendar_name = selected_calendar['name']
            
            print(f"\n✅ Selected: {calendar_name}")
            print(f"📍 Calendar ID: {calendar_id}")
            
            # Get matches
            print("\n🕷️  Scraping Maccabi Haifa matches...")
            matches_json = scrape_haifa_matches()
            matches = json.loads(matches_json)
            
            print(f"Found {len(matches)} matches")
            
            # Add to selected calendar
            calendar_manager = GoogleCalendarManager()
            
            confirm = input(f"\n❓ Add {len(matches)} matches to '{calendar_name}'? (y/N): ")
            if confirm.lower() in ['y', 'yes']:
                added_count = 0
                for match in matches:
                    event_id = calendar_manager.add_event_from_json(match, calendar_id)
                    if event_id:
                        added_count += 1
                
                print(f"\n🎉 Successfully added {added_count}/{len(matches)} matches to '{calendar_name}'!")
            else:
                print("❌ Cancelled")
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Invalid input")
    except Exception as e:
        print(f"❌ Error: {e}")


def create_maccabi_calendar():
    """
    Create a dedicated calendar for Maccabi Haifa matches
    """
    try:
        calendar_manager = GoogleCalendarManager()
        
        # Create new calendar
        calendar_body = {
            'summary': 'Maccabi Haifa Matches',
            'description': 'Automatic calendar for Maccabi Haifa football matches',
            'timeZone': 'Asia/Jerusalem'
        }
        
        created_calendar = calendar_manager.service.calendars().insert(body=calendar_body).execute()
        
        calendar_id = created_calendar['id']
        calendar_name = created_calendar['summary']
        
        print(f"✅ Created new calendar: {calendar_name}")
        print(f"📍 Calendar ID: {calendar_id}")
        
        # Add matches to the new calendar
        print("\n🕷️  Scraping matches...")
        matches_json = scrape_haifa_matches()
        matches = json.loads(matches_json)
        
        print(f"Adding {len(matches)} matches to new calendar...")
        added_count = 0
        for match in matches:
            event_id = calendar_manager.add_event_from_json(match, calendar_id)
            if event_id:
                added_count += 1
        
        print(f"\n🎉 Created calendar and added {added_count}/{len(matches)} matches!")
        return calendar_id
        
    except Exception as e:
        print(f"❌ Error creating calendar: {e}")
        return None


def update_existing_events():
    """
    Update existing calendar events with "not final time" indicator
    """
    print("🔍 Finding your calendars...")
    calendars = list_available_calendars()
    
    if not calendars:
        print("❌ No calendars found or authentication failed")
        return
    
    print("\n📝 Select calendar to update:")
    for i, cal in enumerate(calendars, 1):
        primary_text = " (Your main calendar)" if cal['primary'] else ""
        print(f"{i}. {cal['name']}{primary_text}")
    
    try:
        choice = int(input(f"\nEnter your choice (1-{len(calendars)}): ")) - 1
        if 0 <= choice < len(calendars):
            selected_calendar = calendars[choice]
            calendar_id = selected_calendar['id']
            calendar_name = selected_calendar['name']
            
            print(f"\n✅ Selected: {calendar_name}")
            print(f"📍 Calendar ID: {calendar_id}")
            
            confirm = input(f"\n❓ Update existing Maccabi events in '{calendar_name}' with 'not final time' indicators? (y/N): ")
            if confirm.lower() in ['y', 'yes']:
                calendar_manager = GoogleCalendarManager()
                updated_count = calendar_manager.find_and_update_maccabi_events(calendar_id)
                
                if updated_count > 0:
                    print(f"\n🎉 Successfully updated {updated_count} events!")
                else:
                    print("\n💭 No events needed updating (either no 'not final' matches found or events already updated)")
            else:
                print("❌ Cancelled")
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Invalid input")
    except Exception as e:
        print(f"❌ Error: {e}")


def show_calendar_examples():
    """
    Show code examples for using different calendars
    """
    print("📚 Examples of using different calendars:")
    print("=" * 50)
    
    print("1️⃣  Add to your main calendar (default):")
    print("""
from add_to_calendar import GoogleCalendarManager
calendar_manager = GoogleCalendarManager()
calendar_manager.add_event_from_json(match_data)  # Uses 'primary'
""")
    
    print("2️⃣  Add to a specific calendar by ID:")
    print("""
calendar_manager.add_event_from_json(match_data, 'your_calendar_id_here')
""")
    
    print("3️⃣  Add to a calendar by finding it first:")
    print("""
calendars = calendar_manager.list_calendars()
maccabi_calendar = None
for cal in calendars:
    if 'Maccabi' in cal['name']:
        maccabi_calendar = cal['id']
        break

if maccabi_calendar:
    calendar_manager.add_event_from_json(match_data, maccabi_calendar)
""")
    
    print("4️⃣  Batch add all matches to specific calendar:")
    print("""
from scaper import scrape_haifa_matches
import json

matches = json.loads(scrape_haifa_matches())
calendar_id = 'your_calendar_id_here'

for match in matches:
    calendar_manager.add_event_from_json(match, calendar_id)
""")


if __name__ == "__main__":
    print("🗓️  Maccabi Haifa Calendar Manager")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. List all available calendars")
        print("2. Add matches to a specific calendar")
        print("3. Create new 'Maccabi Haifa' calendar")
        print("4. Update existing events with 'not final time' indicators")
        print("5. Show code examples")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            list_available_calendars()
        elif choice == "2":
            add_matches_to_specific_calendar()
        elif choice == "3":
            create_maccabi_calendar()
        elif choice == "4":
            update_existing_events()
        elif choice == "5":
            show_calendar_examples()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")