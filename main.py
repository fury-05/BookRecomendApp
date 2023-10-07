from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

# Define the Google Books API URL
API_URL = "https://www.googleapis.com/books/v1/volumes"

# Retrieve the API key from Replit Secrets
API_KEY = os.environ.get("REPLIT_SECRET_google_api_key")

# Define options for category, genre, and mood
categories = ["Fiction", "Nonfiction", "Science Fiction", "Mystery", "Fantasy"]
genres = ["Adventure", "Romance", "Thriller", "Science", "History"]
moods = ["Happy", "Sad", "Exciting", "Mysterious", "Inspiring"]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        category = request.form.get("category")
        genre = request.form.get("genre")
        mood = request.form.get("mood")

        # Construct the query for the Google Books API
        query = f"{category}+{genre}+{mood}"

        # Make a request to the API with your API key
        params = {"q": query, "key": API_KEY}
        response = requests.get(API_URL, params=params)

        # Parse the response as JSON
        data = response.json()

        # Extract book recommendations with additional details
        recommendations = []

        for item in data.get("items", []):
            volume_info = item.get("volumeInfo")
            title = volume_info.get("title", "Unknown Title")
            authors = ", ".join(volume_info.get("authors", ["Unknown Author"]))
            release_date = volume_info.get("publishedDate", "Unknown Date")
            book_cover = volume_info.get("imageLinks", {}).get("thumbnail", "No Cover")
            
            recommendations.append({
                "title": title,
                "authors": authors,
                "release_date": release_date,
                "book_cover": book_cover
            })

        return render_template("recommendation.html", recommendations=recommendations)

    return render_template("index.html", categories=categories, genres=genres, moods=moods)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
