import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
from PIL import Image, ImageTk


class MovieSearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎬 Movie Search")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height-80}-8+0")
        self.configure(fg_color="#121212")

        self.movies = self.load_movies("moviedata.csv")
        self.filtered_movies = self.movies
        self.watchlist = []

        self.create_widgets()

    def load_movies(self, file_path):
        try:
            df = pd.read_csv(file_path, encoding='ISO-8859-1')
            df = df.dropna(axis=1, how='all')
            df = df.dropna(subset=["Movie Name", "Release Year", "Genre", "Rating"])
            df.rename(
                columns={
                    "Movie Name": "title",
                    "Release Year": "year",
                    "Genre": "genre",
                    "Rating": "rating",
                    "Director": "director",
                    "Cast and Crew": "cast",
                    "Age Rating": "age_rating",
                    "Duration (Time)": "duration",
                },
                inplace=True,
            )
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
            df = df.dropna(subset=["year"])
            return df.to_dict(orient="records")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.destroy()

    def create_widgets(self):
        dashboard_frame = ctk.CTkFrame(self, width=250, fg_color="#2A2A2A", corner_radius=0)
        dashboard_frame.grid(row=0, column=0, rowspan=3, padx=0, pady=0, sticky="nsew")
        dashboard_frame.grid_rowconfigure(0, weight=1, minsize=70)

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Watchlist", self.show_watchlist),
            ("Settings", self.show_settings),
            ("Sign In", self.sign_in),
            ("Sign Out", self.sign_out),
        ]

        for idx, (text, command) in enumerate(buttons, start=1):
            ctk.CTkButton(
                dashboard_frame, text=text, command=command, fg_color="#1E90FF", text_color="white", hover_color="#4682B4"
            ).grid(row=idx, column=0, pady=10, padx=20, sticky="ew")


        search_frame = ctk.CTkFrame(self, fg_color="#1E1E1E")
        search_frame.grid(row=0, column=1, columnspan=4, padx=20, pady=10, sticky="nsew")

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Search movies...", width=500, height=35)
        self.search_entry.pack(side="left", padx=10)

        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            fg_color="#FF6347",
            hover_color="#FF4500",
            text_color="white",
            font=("Aptos", 18),
            command=self.search_movies,
        )
        search_button.pack(side="left", padx=10)


        sorting_frame = ctk.CTkFrame(self, fg_color="#1E1E1E")
        sorting_frame.grid(row=1, column=1, columnspan=4, padx=20, pady=10, sticky="nsew")

        ctk.CTkLabel(sorting_frame, text="Sort By:", text_color="white").pack(side="left", padx=10)
        ctk.CTkButton(sorting_frame, text="Year", command=lambda: self.sort_movies("year")).pack(side="left", padx=5)
        ctk.CTkButton(sorting_frame, text="Genre", command=lambda: self.sort_movies("genre")).pack(side="left", padx=5)
        ctk.CTkButton(sorting_frame, text="Rating", command=lambda: self.sort_movies("rating")).pack(side="left", padx=5)


        self.movie_frame = ctk.CTkScrollableFrame(self, fg_color="#1E1E1E", corner_radius=10, width=900, height=700)
        self.movie_frame.grid(row=2, column=1, columnspan=4, padx=20, pady=20, sticky="nsew")

        self.update_movie_list()

    def search_movies(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            messagebox.showinfo("Info", "Please enter a search query.")
            return
        self.filtered_movies = [movie for movie in self.movies if query in str(movie["title"]).lower()]
        self.update_movie_list()

    def sort_movies(self, key):
        self.filtered_movies = sorted(self.filtered_movies, key=lambda x: x.get(key, ""))
        self.update_movie_list()

    def update_movie_list(self):
        for widget in self.movie_frame.winfo_children():
            widget.destroy()

        if not self.filtered_movies:
            ctk.CTkLabel(self.movie_frame, text="No movies found.", font=("Arial", 14)).pack(pady=20)
            return

        for movie in self.filtered_movies:
            movie_button = ctk.CTkButton(
                self.movie_frame,
                text=f"{movie['title']}\nYear: {movie['year']} | Genre: {movie['genre']} | Rating: {movie['rating']}",
                fg_color="#333333",
                hover_color="#444444",
                text_color="#FFFFFF",
                font=("Aptos", 16),
                height=80,
                command=lambda m=movie: self.open_movie_details(m),
            )
            movie_button.pack(fill="x", pady=5, padx=10)

    def open_movie_details(self, movie):

        movie_page = ctk.CTkToplevel(self)
        movie_page.title(f"Details - {movie['title']}")
        movie_page.geometry("800x600")
        movie_page.configure(fg_color="#2C3E50")


        movie_page.transient(self) 
        movie_page.focus_force()  
        movie_page.grab_set()  


        poster_frame = ctk.CTkFrame(movie_page, width=200, height=300, fg_color="#34495E")
        poster_frame.grid(row=0, column=0, padx=20, pady=20, rowspan=6)
        poster_label = ctk.CTkLabel(poster_frame, text="Poster\nPlaceholder", font=("Aptos", 16))
        poster_label.pack(expand=True)

        title_label = ctk.CTkLabel(movie_page, text=f"{movie['title']} ({int(movie['year'])})", font=("Aptos", 24, "bold"), text_color="#E74C3C")
        title_label.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        details_text = f"""
    Director: {movie.get('director', 'N/A')}
    Cast and Crew: {movie.get('cast', 'N/A')}
    Genre: {movie.get('genre', 'N/A')}
    Rating: {movie.get('rating', 'N/A')}
    Age Rating: {movie.get('age_rating', 'N/A')}
    Duration: {movie.get('duration', 'N/A')}
    """
        details_label = ctk.CTkLabel(movie_page, text=details_text, font=("Aptos", 16), text_color="#ECF0F1", anchor="w", justify="left")
        details_label.grid(row=1, column=1, sticky="w", padx=10, pady=10)


        if movie in self.watchlist:
            ctk.CTkButton(movie_page, text="Remove from Watchlist", command=lambda: self.remove_from_watchlist(movie)).grid(row=2, column=1, padx=10, pady=10)
        else:
            ctk.CTkButton(movie_page, text="Add to Watchlist", command=lambda: self.add_to_watchlist(movie)).grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkButton(movie_page, text="Close", command=movie_page.destroy, fg_color="#E74C3C", text_color="#FFFFFF").grid(row=3, column=1, padx=10, pady=10)

    def add_to_watchlist(self, movie):
        if movie not in self.watchlist:
            self.watchlist.append(movie)
            messagebox.showinfo("Success", f"'{movie['title']}' added to watchlist.")
            self.show_watchlist()  

    def remove_from_watchlist(self, movie):
        if movie in self.watchlist:
            self.watchlist.remove(movie)
            messagebox.showinfo("Removed", f"'{movie['title']}' removed from watchlist.")
            self.show_watchlist() 
        else:
            messagebox.showinfo("Error", "Movie not in watchlist.")

    def show_dashboard(self):
        self.filtered_movies = self.movies
        self.update_movie_list()

    def show_watchlist(self):
        self.filtered_movies = self.watchlist
        self.update_movie_list()

    def show_settings(self):
        messagebox.showinfo("Settings", "Settings page is under construction.")

    def sign_in(self):
        messagebox.showinfo("Sign In", "Sign-in functionality coming soon.")

    def sign_out(self):
        messagebox.showinfo("Sign Out", "Sign-out functionality coming soon.")


if __name__ == "__main__":
    app = MovieSearchApp()
    app.mainloop()

