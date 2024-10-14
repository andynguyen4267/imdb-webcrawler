import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import argparse
from collections import Counter

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="IMDb Top Movies Scraper")
parser.add_argument('--top', type=int, default=10, help="Number of top movies to scrape (default: 10)")
parser.add_argument('--plot', choices=['bar', 'hist', 'pie'], default='bar', help="Type of plot to display: 'bar', 'hist', or 'pie' (default: bar)")
parser.add_argument('--export', choices=['csv', 'json', 'excel'], help="Format to export data: 'csv', 'json', or 'excel'")
parser.add_argument('--filename', type=str, default='imdb_top_movies', help="Filename for exported data (without extension)")

args = parser.parse_args()

# Set the user-agent to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = "https://www.imdb.com/chart/top"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the JSON-LD script
    script = soup.find('script', type='application/ld+json')
    
    if script:
        json_data = json.loads(script.string)
        
        # Extract movie data
        movie_data = []
        genre_data = []
        
        for index, item in enumerate(json_data['itemListElement'], start=1):
            movie = item['item']
            title = movie['name']
            rating = float(movie['aggregateRating']['ratingValue'])
            genres = movie.get('genre', [])
            
            movie_data.append({
                'Rank': index,
                'Title': title,
                'Rating': rating,
                'Genres': genres if isinstance(genres, list) else [genres]  # Ensure genres is a list
            })
            
            # Collect genres for pie chart
            genre_data.extend(genres if isinstance(genres, list) else [genres])
        
        # Create a DataFrame
        df = pd.DataFrame(movie_data)
        
        # Step 1: Select the number of top movies based on the --top argument
        top_movies = df.head(args.top)

        plt.figure(figsize=(10,6))
        
        if args.plot == 'bar':
            sns.barplot(x='Rating', y='Title', data=top_movies, palette='viridis')
            plt.title(f'Top {args.top} Movies by IMDb Rating')
            plt.xlabel('IMDb Rating')
            plt.ylabel('Movie Title')

        elif args.plot == 'hist':
            sns.histplot(df['Rating'], kde=True, bins=10)
            plt.title('Distribution of IMDb Ratings')
            plt.xlabel('IMDb Rating')
            plt.ylabel('Frequency')

        elif args.plot == 'pie':
            # Get the most common 10 genres
            genre_counts = Counter(genre_data).most_common(10)
            labels, sizes = zip(*genre_counts)
            
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('Set3'))
            plt.title(f'Distribution of Genres in Top {args.top} IMDb Movies')

        plt.show()

        # Export the data based on the --export argument
        if args.export:
            file_name = args.filename

            if args.export == 'csv':
                top_movies.to_csv(f"{file_name}.csv", index=False)
                print(f"Data exported as {file_name}.csv")

            elif args.export == 'json':
                top_movies.to_json(f"{file_name}.json", orient='records', lines=True)
                print(f"Data exported as {file_name}.json")

            elif args.export == 'excel':
                top_movies.to_excel(f"{file_name}.xlsx", index=False)
                print(f"Data exported as {file_name}.xlsx")

    else:
        print("JSON-LD script not found.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
