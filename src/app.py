from flask import Flask, request, jsonify, send_file, render_template
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Save chart in memory for retrieval in another route
img = BytesIO()

# Serve the frontend HTML page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')  # Make sure 'index.html' is in a 'templates' folder

@app.route('/', methods=['POST'])
def scrape():
    global img  # Access the global img object
    data = request.json
    top_n = data['top']
    plot_type = data['plot']
    export_format = data['export']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = "https://www.imdb.com/chart/top"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Scrape logic for movie data (replace this with your actual scraping code)
        movie_data = [{'Rank': i+1, 'Title': f'Movie {i+1}', 'Rating': 8.5 + i*0.1} for i in range(int(top_n))]
        df = pd.DataFrame(movie_data)

        # Plotting logic
        plt.figure(figsize=(10,6))
        if plot_type == 'bar':
            sns.barplot(x='Rating', y='Title', data=df, palette='viridis')
        elif plot_type == 'hist':
            sns.histplot(df['Rating'], kde=True, bins=10)
        elif plot_type == 'pie':
            genres = ["Action", "Drama", "Comedy", "Thriller", "Adventure"]
            counts = [10, 20, 30, 25, 15]
            plt.pie(counts, labels=genres, autopct='%1.1f%%')

        # Save the plot to the BytesIO object
        img = BytesIO()  # Create a new BytesIO object for each request
        plt.savefig(img, format='png')
        plt.close()  # Clear the plot
        img.seek(0)  # Reset pointer to start of BytesIO object

        # Save the scraped data to a file in the requested format
        file_name = f"imdb_top_movies.{export_format}"
        file_path = os.path.join("downloads", file_name)
        
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        if export_format == 'csv':
            df.to_csv(file_path, index=False)
        elif export_format == 'json':
            df.to_json(file_path, orient='records')
        elif export_format == 'excel':
            df.to_excel(file_path, index=False)

        return jsonify({
            "chart_url": "/chart.png",  # Dynamic URL to retrieve the chart
            "download_url": f"/download/{file_name}"  # File download URL
        })

    return jsonify({"error": "Failed to scrape the page."}), 400

# Route to serve the chart image
@app.route('/chart.png')
def serve_chart():
    global img
    img.seek(0)  # Ensure the pointer is reset to the start of the image
    return send_file(img, mimetype='image/png')

# Route to download the generated file
@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join("downloads", filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)
