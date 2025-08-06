#!/usr/bin/env python3
"""
One-time setup script for Maccabi Haifa calendar sync
Creates initial state and tests the sync functionality
"""

import json
import os
from datetime import datetime
from add_to_calendar import GoogleCalendarManager
from scaper import scrape_haifa_matches


def setup_initial_sync():
    """Setup initial sync state"""
    print("🔧 Setting up Maccabi Haifa Calendar Auto-Sync")
    print("=" * 50)
    
    # Check credentials
    if not os.path.exists("credentials.json"):
        print("❌ ERROR: credentials.json not found")
        print("Please download it from Google Cloud Console first")
        return False
    
    print("✅ Found credentials.json")
    
    # Test calendar access
    try:
        print("🔐 Testing Google Calendar access...")
        calendar_manager = GoogleCalendarManager()
        calendars = calendar_manager.list_calendars()
        
        # Find מכבי calendar
        maccabi_calendar = None
        for cal in calendars:
            if 'מכבי' in cal['name']:
                maccabi_calendar = cal
                break
        
        if maccabi_calendar:
            print(f"✅ Found מכבי calendar: {maccabi_calendar['name']}")
            print(f"   Calendar ID: {maccabi_calendar['id']}")
        else:
            print("⚠️  מכבי calendar not found - will use primary calendar")
        
    except Exception as e:
        print(f"❌ Calendar access test failed: {e}")
        return False
    
    # Test website scraping
    try:
        print("🕷️  Testing website scraping...")
        matches_json = scrape_haifa_matches()
        matches = json.loads(matches_json)
        print(f"✅ Successfully scraped {len(matches)} matches")
        
        # Show sample matches
        print("\nSample matches:")
        for i, match in enumerate(matches[:3]):
            not_final = f" {match['not_final_time']}" if match.get('not_final_time') else ""
            print(f"  {i+1}. {match['date_day']}/{match['date_month']} {match['time']} - {match['home_team']} vs {match['away_team']}{not_final}")
        
        if len(matches) > 3:
            print(f"  ... and {len(matches) - 3} more matches")
            
    except Exception as e:
        print(f"❌ Website scraping test failed: {e}")
        return False
    
    # Create initial state file
    try:
        print("💾 Creating initial sync state...")
        
        # Calculate initial hash
        import hashlib
        sorted_matches = sorted(matches, key=lambda x: (x['date_month'], x['date_day'], x['time']))
        match_string = ""
        for match in sorted_matches:
            match_string += f"{match['date_day']}-{match['date_month']}-{match['time']}-"
            match_string += f"{match['home_team']}-{match['away_team']}-{match['venue']}-"
            match_string += f"{match['competition']}-{match.get('not_final_time', '')}"
        
        initial_hash = hashlib.md5(match_string.encode('utf-8')).hexdigest()
        
        initial_state = {
            "last_hash": initial_hash,
            "last_sync": datetime.now().isoformat(),
            "last_match_count": len(matches),
            "event_ids": {},
            "setup_date": datetime.now().isoformat(),
            "setup_version": "1.0"
        }
        
        with open("sync_state.json", "w", encoding="utf-8") as f:
            json.dump(initial_state, f, ensure_ascii=False, indent=2)
        
        print("✅ Initial sync state created")
        
    except Exception as e:
        print(f"❌ Failed to create initial state: {e}")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: ./sync_maccabi.sh run         # Test sync once")
    print("2. Run: ./sync_maccabi.sh setup       # Setup automatic hourly sync")
    print("3. Run: ./sync_maccabi.sh status      # Check sync status")
    print("4. Run: ./sync_maccabi.sh logs        # View sync logs")
    
    return True


if __name__ == "__main__":
    setup_initial_sync()