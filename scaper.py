import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz


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
    url = "https://www.mhaifafc.com/matches"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    matches = []

    for match_div in soup.select('div.flex.border-b'):
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
            venue = match_div.select_one('div.h-6 span.text-grayLight').text.strip()

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


            matches.append({
                "date_day": date_day,
                "date_month": date_month,
                "time": time,
                "competition": competition,
                "venue": venue,
                "home_team": home_team,
                "away_team": away_team,
                "not_final_time": not_final_indicator
            })
        except Exception as e:
            print(f"Skipping a match due to error: {e}")
            continue

    return json.dumps(matches, ensure_ascii=False, indent=2)


# Example usage
if __name__ == "__main__":
    print(scrape_haifa_matches())
