import csv
from movie import Movie 


class MovieCollection:
    def __init__(self):
        self.movies = []

    def add_movie(self, movie):
        if isinstance(movie, Movie):
            self.movies.append(movie)
        else:
            raise ValueError("Only Movie instances can be added.")

    def remove_movie(self, title):
        initial_count = len(self.movies)
        self.movies = [movie for movie in self.movies if movie.title.lower() != title.lower()]
        if len(self.movies) < initial_count:
            print(f"Removed movie: {title}")
        else:
            print(f"No movie found with title: {title}")

    def update_movie_rating(self, title, new_rating):
        movie = self.get_movie_by_title(title)
        if movie:
            movie.update_rating(new_rating)
            print(f"Updated rating for '{title}' to {new_rating}.")
        else:
            print(f"No movie found with title: {title}")

    def get_movie_by_title(self, title):
        for movie in self.movies:
            if movie.title.lower() == title.lower():
                return movie
        return None

    def filter_by_genre(self, genre):
        return [movie for movie in self.movies if genre.lower() in [g.strip().lower() for g in movie.genre.split(",")]]

    def filter_by_year(self, year):
        return [movie for movie in self.movies if movie.release_year == year]

    def get_top_rated_movies(self, threshold=8.0):
        return [movie for movie in self.movies if movie.is_top_rated(threshold)]

    def generate_report(self):
        report = []
        genres = set()
        for movie in self.movies:
            genres.update([g.strip() for g in movie.genre.split(",")])

        for genre in genres:
            genre_movies = self.filter_by_genre(genre)
            if genre_movies:
                avg_rating = sum(movie.imdb_rating for movie in genre_movies) / len(genre_movies)
                report.append(f"Average rating for {genre}: {avg_rating:.2f}")
            else:
                report.append(f"No movies found for genre: {genre}")

        return "\n".join(report)

    def save_to_csv(self, filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file,
                                    fieldnames=["title", "release_year", "genre", "imdb_rating", "director", "cast"])
            writer.writeheader()  
            for movie in self.movies:
            
                cast_str = ", ".join(movie.cast) if movie.cast else "N/A"
                writer.writerow({
                    "title": movie.title,
                    "release_year": movie.release_year,
                    "genre": movie.genre,
                    "imdb_rating": movie.imdb_rating,
                    "director": movie.director or "N/A",
                    "cast": cast_str 
                })
        print(f"Movie collection saved to '{filename}'.")

    def __repr__(self):
        return f"MovieCollection({len(self.movies)} movies)"


if __name__ == "__main__":
    collection = MovieCollection()
    movie1 = Movie("Inception", 2010, "Action, Sci-Fi", 8.8, "Christopher Nolan",
                   ["Leonardo DiCaprio", "Joseph Gordon-Levitt"])
    movie2 = Movie("The Godfather", 1972, "Crime, Drama", 9.2, "Francis Ford Coppola", ["Marlon Brando", "Al Pacino"])

    collection.add_movie(movie1)
    collection.add_movie(movie2)

    print(collection)
    print(collection.generate_report())

    collection.save_to_csv("movies_report.csv")
