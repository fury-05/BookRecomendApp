from flask import Flask, request, render_template
import requests
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

# Retrieve the API key from Replit Secrets for Google Books API
API_KEY = os.environ.get("REPLIT_SECRET_google_api_key")

# Retrieve the API key from Replit Secrets for The New York Times Best Sellers API
NYT_API_KEY = os.environ.get("nyt_api_key")

# Define the Google Books API URL
API_URL = "https://www.googleapis.com/books/v1/volumes"

# Define options for category, genre, and mood
categories = ["Fiction", "Nonfiction", "Science Fiction", "Mystery", "Fantasy"]
genres = ["Adventure", "Romance", "Thriller", "Science", "History"]
moods = ["Happy", "Sad", "Exciting", "Mysterious", "Inspiring"]

# Function to fetch and process trending book data from The New York Times Best Sellers API
def fetch_trending_books():
    try:
        url = f"https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key={NYT_API_KEY}"

        trending_response = requests.get(url)
        trending_response.raise_for_status()

        trending_data = trending_response.json()

        trending_books = []

        heading = "Top Trending Books from The New York Times for Today"
        for i, book in enumerate(trending_data.get("results", {}).get("books", [])):
            title = book.get("title", "Unknown Title")
            authors = ", ".join(book.get("author", ["Unknown Author"])).replace(",", "")
            release_date = book.get("first_publish_date", "Unknown Date")
            book_cover = book.get("book_image", "No Cover")

            trending_books.append({
                "title": title,
                "authors": authors,
                "release_date": release_date,
                "book_cover": book_cover,
            })

            if i == 9:  # Limit to the top 10 trending books
                break

        return heading, trending_books
    except Exception as e:
        # Print the exception for debugging
        print(f"Error fetching trending books: {e}")
        return "", []  # Return an empty list and an empty heading in case of an error

# Function to process book data and generate recommendations
def process_books(data, category, genre, mood):
    recommendations = []
    book_descriptions = []

    for item in data.get("items", []):
        volume_info = item.get("volumeInfo")
        title = volume_info.get("title", "Unknown Title")
        authors = ", ".join(volume_info.get("authors", ["Unknown Author"])).replace(",", "")
        release_date = volume_info.get("publishedDate", "Unknown Date")
        book_cover = volume_info.get("imageLinks", {}).get("thumbnail", "No Cover")
        description = volume_info.get("description", "")

        book_info = f"{title} {authors} {release_date} {description}"
        book_descriptions.append(book_info)

        recommendations.append({
            "title": title,
            "authors": authors,
            "release_date": release_date,
            "book_cover": book_cover,
        })

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(book_descriptions)

    user_preference = f"{category} {genre} {mood}"
    user_vector = vectorizer.transform([user_preference])

    cosine_similarities = cosine_similarity(user_vector, tfidf_matrix)

    similar_books_indices = cosine_similarities.argsort()[0][::-1]
    top_similar_indices = similar_books_indices[:10]

    final_recommendations = [recommendations[i] for i in top_similar_indices]

    return final_recommendations

@app.route("/", methods=["GET", "POST"])
def index():
    heading, trending_books = fetch_trending_books()  # Fetch top 10 trending books from The New York Times

    if request.method == "POST":
        category = request.form.get("category")
        genre = request.form.get("genre")
        mood = request.form.get("mood")

        query = f"{category}+{genre}+{mood}"

        params = {"q": query, "key": API_KEY}
        response = requests.get(API_URL, params=params)

        data = response.json()

        enhanced_recommendations = process_books(data, category, genre, mood)

        return render_template("recommendation.html", enhanced_recommendations=enhanced_recommendations, trending_books=trending_books, heading=heading, raw_response=data)

    return render_template("index.html", categories=categories, genres=genres, moods=moods, trending_books=trending_books, heading=heading)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
