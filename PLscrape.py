##importing all required libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from io import StringIO

all_teams = []

# Fetch HTML from the La Liga stats page
html = requests.get('https://fbref.com/en/comps/12/La-Liga-Stats').text
soup = BeautifulSoup(html, 'lxml')

# Get the first table with the class 'stats_table'
table = soup.find_all('table', class_='stats_table')[0]

# Retrieve all links from the table
links = table.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if '/squads/' in l]  # Filter links to get only those leading to squad pages

# Format full URLs
team_urls = [f"https://fbref.com{l}" for l in links]

# Loop through all team URLs
for team_url in team_urls: 
    team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")  # Isolate the team name
    data = requests.get(team_url).text
    soup = BeautifulSoup(data, 'lxml')
    
    # Get the first table on the team page
    stats = soup.find_all('table', class_='stats_table')[0]
    
    # Read the table using pd.read_html() after using StringIO to avoid warnings
    html_str = str(stats)
    html_data = StringIO(html_str)
    
    team_data = pd.read_html(html_data)[0]
    
    # Check if the DataFrame has a multi-level header and flatten it
    if isinstance(team_data.columns, pd.MultiIndex):
        team_data.columns = ['_'.join(col).strip() for col in team_data.columns.values]
    
    # Add the team name to the DataFrame
    team_data["Team"] = team_name
    
    # Append the DataFrame to the list of all teams
    all_teams.append(team_data)
    
    # Wait to avoid being blocked
    time.sleep(1)

# Concatenate all teams' DataFrames
stat_df = pd.concat(all_teams)

# Save the DataFrame to a CSV file
stat_df.to_csv("stats.csv", index=False)

# To view the first few rows of the DataFrame (optional)
print(stat_df.head())