class Movie:
    def __init__(self, title, release_year, genre, imdb_rating, director=None, cast=None):
        self.title = title
        self.release_year = release_year
        self.genre = genre
        self.imdb_rating = imdb_rating
        self.director = director
        self.cast = cast if cast else [] 
        self.rating_history = []  

    def add_rating(self, rating, date):
        self.rating_history.append({'rating': rating, 'date': date})

    def get_rating_trend(self):
        return [(entry['date'], entry['rating']) for entry in self.rating_history]

    def update_rating(self, new_rating):
        self.imdb_rating = new_rating

    def is_top_rated(self, threshold=8.0):
        return self.imdb_rating >= threshold

    def __repr__(self):
        cast = ", ".join(self.cast) if self.cast else "No cast information"
        return f"{self.title} ({self.release_year}) - {self.genre} - Rating: {self.imdb_rating} - Cast: {cast}"
