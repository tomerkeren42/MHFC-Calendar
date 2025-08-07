"""
Maccabi Haifa FC Match Scraper

Scrapes match data from https://www.mhaifafc.com/matches using a dual-request
strategy to capture all games, including those behind JavaScript "Load More".

Uses two date filters to bypass dynamic content loading and get complete match data.
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import pytz
import urllib.parse


def convert_utc_to_israel_time(time_str):
    """Convert UTC time string (HH:MM) to Israel time"""
    try:
        # Parse the time string
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        
        # Create a datetime with today's date and the parsed time in UTC
        utc_tz = pytz.UTC
        israel_tz = pytz.timezone('Asia/Jerusalem')
        
        # Use a dummy date for conversion
        dummy_date = datetime.now().date()
        utc_datetime = datetime.combine(dummy_date, time_obj).replace(tzinfo=utc_tz)
        
        # Convert to Israel time
        israel_datetime = utc_datetime.astimezone(israel_tz)
        
        # Return formatted time string
        return israel_datetime.strftime("%H:%M")
    except Exception as e:
        print(f"Error converting time {time_str}: {e}")
        return time_str  # Return original if conversion fails


def scrape_haifa_matches():
    """
    Scrapes all Maccabi Haifa matches using dual date filters.
    
    Makes two requests: current date and 4 months forward.
    This bypasses JavaScript "Load More" to capture all available games.
    """
    base_url = "https://www.mhaifafc.com/matches"
    tab_param = urllib.parse.quote('משחקים הבאים')
    
    # Calculate dynamic dates
    now = datetime.now()
    current_date = now.strftime("%d/%m/%Y %H:%M")
    
    # Add 4 months to current date
    future_date = now + timedelta(days=120)  # Approximately 4 months
    future_date_str = future_date.strftime("%d/%m/%Y 00:00")
    
    print(f"Using current date: {current_date}")
    print(f"Using future date: {future_date_str}")
    
    # Request 1: Games from current date onwards
    filters1 = f'{{"date":{{"startDate":"{current_date}","endDate":""}},"league":"","session":"","gamesDirection":"1","againstTeam":""}}'
    encoded_filters1 = urllib.parse.quote(filters1)
    url1 = f'{base_url}?filters={encoded_filters1}&tab={tab_param}'
    
    # Request 2: Games from 4 months forward (captures additional games)
    filters2 = f'{{"date":{{"startDate":"{future_date_str}","endDate":""}},"league":"","session":"","gamesDirection":"1","againstTeam":""}}'
    encoded_filters2 = urllib.parse.quote(filters2)
    url2 = f'{base_url}?filters={encoded_filters2}&tab={tab_param}'
    
    all_matches = []
    processed_games = set()  # To avoid duplicates
    
    # Process both requests
    for i, url in enumerate([url1, url2], 1):
        try:
            print(f"Fetching games from request {i}...")
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            match_divs = soup.select('div.flex.border-b')
            print(f"Found {len(match_divs)} games in request {i}")
            
            for match_div in match_divs:
                match_data = parse_match_div(match_div)
                if match_data:
                    # Create a unique identifier for the match to avoid duplicates
                    match_key = f"{match_data['date_day']}-{match_data['date_month']}-{match_data['home_team']}-{match_data['away_team']}"
                    
                    if match_key not in processed_games:
                        all_matches.append(match_data)
                        processed_games.add(match_key)
                        
        except Exception as e:
            print(f"Error in request {i}: {e}")
            continue
    
    print(f"Total unique games found: {len(all_matches)}")
    return json.dumps(all_matches, ensure_ascii=False, indent=2)


def parse_match_div(match_div):
    """Extract match data from a match div element"""
    try:
        # Date
        date_container = match_div.select_one('div.bg-grayMediumLight')
        date_day = date_container.select_one('span.text-4xl').text.strip()
        date_month = date_container.select_one('span.text-xl').text.strip()
        
        # Check for "not final time" indicator (לא סופי)
        date_container_text = date_container.get_text()
        not_final_indicator = ""
        if "לא סופי" in date_container_text or "לא סופי(" in date_container_text:
            # Extract the bracket text
            import re
            bracket_match = re.search(r'\([^)]*לא סופי[^)]*\)', date_container_text)
            if bracket_match:
                not_final_indicator = bracket_match.group(0)

        # Time
        time_raw = match_div.select_one('div.text-4xl').text.strip()
        time = convert_utc_to_israel_time(time_raw)

        # Competition
        competition = match_div.select_one('div.h-6 span.lg\\:text-xl').text.strip()
        if "WINNER" in competition:
            competition = "ליגה"
        
        # Venue
        venue = match_div.select_one('div.h-6 span.text-grayLight')
        if venue is None:
            venue = "לא ידוע"
        else:
            venue = venue.text.strip()

        # Teams
        team_spans = match_div.select('span.lg\\:text-xl')
        if len(team_spans) >= 3:
            away_team = team_spans[1].text.strip()
            home_team = team_spans[2].text.strip()
        else:
            away_team = home_team = None

        if away_team == "מכבי חיפה":
            away_team = "מכבי"
        elif home_team == "מכבי חיפה":
            home_team = "מכבי"

        return {
            "date_day": date_day,
            "date_month": date_month,
            "time": time,
            "competition": competition,
            "venue": venue,
            "home_team": home_team,
            "away_team": away_team,
            "not_final_time": not_final_indicator
        }
    except Exception as e:
        print(f"Skipping a match due to error: {e}")
        return None


if __name__ == "__main__":
    print(scrape_haifa_matches())
