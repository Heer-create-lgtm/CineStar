import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
from PIL import Image, ImageTk
import requests
import io
import json
import os
import atexit


class MovieSearchApp(ctk.CTk):
    
    def __init__(self, current_user=None):
        super().__init__()
        self.title("Movie Search")
        screen_width = self.winfo_screenwidth()
        self.movies_data = pd.read_csv('1000_movies.csv')
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height-80}-8+0")
        self.configure(fg_color="#1C1C1C")
        
       
        self.movies = self.load_movies("moviedata.csv")
        
      
        self.search_movies_dataset = self.load_movies("1000_movies.csv")
        
        self.filtered_movies = self.movies
        self.watchlist = []
        self.current_user = current_user
        self.users = {}
        self.discussions_file = "discussions.json"
        self.discussions = self.load_discussions()

        
        self.create_widgets()
        atexit.register(self.save_discussions)
    
    def load_discussions(self):
        try:
            with open(self.discussions_file, "r") as file:
                discussions = json.load(file)
            
        
            for movie, comments in discussions.items():
                if not isinstance(comments, list):  
                    discussions[movie] = []
                else:
                    
                    discussions[movie] = [
                        comment for comment in comments
                        if isinstance(comment, dict) and "username" in comment and "message" in comment
                    ]
            
            return discussions
        except (FileNotFoundError, json.JSONDecodeError):
            return {} 


    def save_discussions(self):
        with open(self.discussions_file, "w") as file:
            json.dump(self.discussions, file, indent=4)

    def load_movies(self, file_path):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file '{file_path}' does not exist.")
            
            df = pd.read_csv(file_path, encoding="ISO-8859-1")
            df = df.dropna(axis=1, how="all")
            essential_columns = ["Movie Name", "Release Year", "Genre", "Rating", "Director"]
            missing_columns = [col for col in essential_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"The following essential columns are missing in the CSV: {missing_columns}")
            df = df.dropna(subset=essential_columns)
            df.rename(columns={
                "Movie Name": "title",
                "Release Year": "year",
                "Genre": "genre",
                "Rating": "rating",
                "Cast and Crew": "cast_and_crew",
                "Director": "director",
                "Age Rating": "age_rating",
                "Duration (Time)": "duration"
            }, inplace=True)
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
            df = df.dropna(subset=["year"])
            df["year"] = df["year"].astype(int)
            
            api_key = "5d8c34f2"
            df["poster"] = df["title"].apply(
                lambda title: f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
            )
            return df.to_dict(orient="records")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load movie data: {str(e)}")
            self.destroy()

    def create_widgets(self):
        
        self.grid_rowconfigure(0, weight=1, minsize=60)
        self.grid_rowconfigure(1, weight=1, minsize=60)
        self.grid_rowconfigure(2, weight=2, minsize=200)
        self.grid_columnconfigure(0, weight=0, minsize=300)
        self.grid_columnconfigure(1, weight=1, minsize=250)
        self.grid_columnconfigure(2, weight=1, minsize=250)
        self.grid_columnconfigure(3, weight=1, minsize=200)
        self.grid_columnconfigure(4, weight=1, minsize=100)
        self.grid_columnconfigure(5, weight=1, minsize=250)
            

        self.dashboard_frame = ctk.CTkFrame(self, fg_color="#1C1C1C", width=250, height=700)
        self.dashboard_frame.grid(row=0, column=0, rowspan=3, padx=0, pady=0, sticky="nsew")
        for i in range(11):
            self.dashboard_frame.grid_rowconfigure(i, weight=1)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        
        buttons = [("Dashboard", self.dashboard_action),
                   ("Watchlist", self.watchlist_action),
                   ("Logout", self.logout_action)]
        
        for idx, (text, command) in enumerate(buttons):
            ctk.CTkButton(
                self.dashboard_frame,
                text=text,
                font=("Aptos", 20),
                corner_radius=0,
                fg_color="#1C1C1C",
                hover_color="#2E2E2E",
                text_color="#FFFFFF",
                border_width=1,
                command=command
            ).grid(row=idx + 2, column=0, sticky="nsew", pady=0, padx=5)
        

        self.search_frame = ctk.CTkFrame(self, fg_color="#2E2E2E")
        self.search_frame.grid(row=0, column=2, columnspan=4, padx=10, pady=10, sticky="e")
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            border_width=1,
            placeholder_text="Search for movies...",
            width=330,
            height=35,
            fg_color="#3E3E3E",
            text_color="#FFFFFF",
            corner_radius=5
        )
        self.search_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            self.search_frame,
            text="Search",
            font=("Aptos", 18),
            width=100,
            height=35,
            fg_color="#1ABC9C",
            hover_color="#16A085",
            text_color="#FFFFFF",
            command=self.search_movies
        )
        search_button.pack(side="left", padx=5)

        self.sort_filter_frame = ctk.CTkFrame(self, fg_color="#2E2E2E")
        self.sort_filter_frame.grid(row=1, column=2, columnspan=4, padx=10, pady=10, sticky="e")
        
        self.year_var = ctk.StringVar(value="Sort by year")
        
        sort_year_dropdown = ctk.CTkComboBox(
            self.sort_filter_frame,
            border_width=1,
            border_color="#1ABC9C",
            button_color="#1ABC9C",
            button_hover_color="#16A085",
            variable=self.year_var,
            height=30,
            values=["Latest to Oldest", "Oldest to Latest"],
            command=lambda _: self.sort_by_year(),
        )
        
        sort_year_dropdown.pack(side="left", padx=5)
        
        self.genre_var = ctk.StringVar(value="Genre")
        
        genre_dropdown = ctk.CTkComboBox(
            self.sort_filter_frame,
            border_width=1,
            border_color="#1ABC9C",
            button_color="#1ABC9C",
            button_hover_color="#16A085",
            variable=self.genre_var,
            height=30,
            values=[
                "All", "Action", "Crime", "Drama", "Romance", "Horror", "Sci-Fi",
                "Thriller", "Biography", "History", "War", "Adventure", "Fantasy",
                "Family", "Western", "Animation", "Mystery", "Music"
            ],
            command=lambda _: self.filter_by_genre(),
        )
        
        genre_dropdown.pack(side="left", padx=5)

        self.rating_var = ctk.StringVar(value="Rating")
        rating_dropdown = ctk.CTkComboBox(
            self.sort_filter_frame,
            border_width=1,
            border_color="#1ABC9C",
            button_color="#1ABC9C",
            button_hover_color="#16A085",
            variable=self.rating_var,
            height=30,
            values=["All", "9+", "8-9", "7-8", "6-7", "Below 6"],
            command=lambda _: self.filter_by_rating(),
        )
        rating_dropdown.pack(side="left", padx=5)
        
        reset_button = ctk.CTkButton(
            self.sort_filter_frame,
            text="Reset",
            font=("Aptos", 15),
            width=50,
            height=30,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            text_color="#FFFFFF",
            command=self.reset_filters
        )
        reset_button.pack(side="left", padx=5)
        
        logo_path = "logo.png"  # Path to your logo file
        logo_image = Image.open(logo_path)
        logo_image_resized = logo_image.resize((70, 70))  # Resize to fit the design
        logo_ctk_image = ctk.CTkImage(logo_image_resized,size=(70, 70))

        self.logo_label = ctk.CTkLabel(self, image=logo_ctk_image, text="", fg_color="#1C1C1C")
        self.logo_label.grid(row=0, column=0,rowspan=2, padx=20, pady=5, sticky="ws")
        
        self.label = ctk.CTkLabel(self, text="CineStar+",font=("Aptos", 34), fg_color="#1C1C1C")
        self.label.grid(row=0, column=0,rowspan=2, padx=0, pady=10, sticky="es")
      
        self.watchlist_controls_frame = ctk.CTkFrame(self, fg_color="#2E2E2E")
        self.watchlist_controls_frame.grid(row=1, column=1, columnspan=4, padx=10, pady=10, sticky="w")
        self.watchlist_controls_frame.grid_remove() 
        

        self.watchlist_search_entry = ctk.CTkEntry(
            self.watchlist_controls_frame,
            border_width=1,
            placeholder_text="Search in Watchlist...",
            width=300,
            height=35,
            fg_color="#3E3E3E",
            text_color="#FFFFFF",
            corner_radius=5,
        )
        self.watchlist_search_entry.pack(side="left", padx=10)
        
        self.watchlist_search_button = ctk.CTkButton(
            self.watchlist_controls_frame,
            text="Search",
            font=("Aptos", 15),
            fg_color="#1ABC9C",
            hover_color="#16A085",
            text_color="#FFFFFF",
            command=lambda: self.filter_watchlist(self.watchlist_search_entry.get()),
        )
        self.watchlist_search_button.pack(side="left", padx=5)

        self.watchlist_sort_var = ctk.StringVar(value="Sort by")
        self.watchlist_sort_dropdown = ctk.CTkComboBox(
            self.watchlist_controls_frame,
            variable=self.watchlist_sort_var,
            height=35,
            values=["Title (A-Z)", "Title (Z-A)", "Year (Newest)", "Year (Oldest)"],
            command=lambda _: self.sort_watchlist(self.watchlist_sort_var.get()),
        )
        self.watchlist_sort_dropdown.pack(side="left", padx=10)
        
        export_button = ctk.CTkButton(
            self.watchlist_controls_frame,
            text="genre avg rating",
            font=("Aptos", 15),
            fg_color="#1ABC9C",
            hover_color="#16A085",
            text_color="#FFFFFF",
            command=self.export_watchlist_to_csv
        )
        export_button.pack(side="left", padx=10)

        self.movie_frame = ctk.CTkScrollableFrame(self, fg_color="#2E2E2E", width=900, height=700, corner_radius=10)
        self.movie_frame.grid(row=2, column=1, columnspan=5, padx=20, pady=20, sticky="nsew")
        
        for i in range(5):
            self.movie_frame.grid_columnconfigure(i, weight=1)
        
        self.update_movie_list()
    
    def show_discussion(self, movie,details_window):
        movie_title = movie["title"]
        discussion_window = ctk.CTkToplevel(self)
        discussion_window.title(f"Discussion - {movie_title}")
        discussion_window.geometry("600x400")
        discussion_window.configure(fg_color="#1B1B1B")
        discussion_window.transient(details_window)
      
        discussions = self.discussions.get(movie_title, [])


        header_label = ctk.CTkLabel(
            discussion_window,
            text=f"Discussion for {movie_title}",
            font=("Arial", 20, "bold"),
            text_color="#FFFFFF"
        )
        header_label.pack(pady=10)

        
        display_frame = ctk.CTkScrollableFrame(discussion_window, width=500, height=200, fg_color="#2E2E2E")
        display_frame.pack(pady=10)

        for discussion in discussions:
            comment_label = ctk.CTkLabel(
                display_frame,
                text=f"{discussion['username']}: {discussion['message']}",
                font=("Arial", 14),
                text_color="#FFFFFF",
                anchor="w"
            )
            comment_label.pack(anchor="w", padx=10, pady=5)

  
        input_frame = ctk.CTkFrame(discussion_window, fg_color="#2E2E2E")
        input_frame.pack(pady=10, fill="x", expand=True)

    
        comment_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Write your comment here...",
            width=400,
            fg_color="#3E3E3E",
            text_color="#FFFFFF"
        )
        comment_entry.pack(side="left", padx=10, pady=10)


        def submit_comment():
            new_comment = comment_entry.get().strip()
            if new_comment:
                username = self.current_user or "Guest"  
                
                
                self.discussions.setdefault(movie_title, []).append({
                    "username": username,
                    "message": new_comment
                })

                
                self.save_discussions()

                messagebox.showinfo("Success", "Your comment has been added!")
                discussion_window.destroy()
                self.show_discussion(movie)  

        submit_button = ctk.CTkButton(
            input_frame,
            text="Post",
            font=("Arial", 14),
            fg_color="#1ABC9C",
            hover_color="#16A085",
            text_color="#FFFFFF",
            command=submit_comment
        )
        submit_button.pack(side="left", padx=10)

    
    def save_discussion(self, movie_title):
       
        message = self.discussion_input.get().strip()
        if not message:
            messagebox.showinfo("Info", "Message cannot be empty!")
            return

       
        username = self.current_user or "Guest"

   
        discussions = self.load_discussions()

        if movie_title not in discussions:
            discussions[movie_title] = []

        
        discussions[movie_title].append({"username": username, "message": message})

      
        with open("discussions.json", "w") as file:
            json.dump(discussions, file, indent=4)

      
        self.discussion_input.delete(0, "end")
        self.load_movie_discussions(movie_title)


    def load_movie_discussions(self, movie_title):
      
        discussions = self.load_discussions()
        

        for widget in self.discussion_frame.winfo_children():
            widget.destroy()

     
        if movie_title in discussions:
            for discussion in discussions[movie_title]:
                username = discussion["username"]
                message = discussion["message"]
                formatted_message = f"{username}: {message}"  

              
                label = ctk.CTkLabel(
                    self.discussion_frame,
                    text=formatted_message,
                    font=("Arial", 14),
                    text_color="#FFFFFF",
                    anchor="w",
                    justify="left",
                    wraplength=500,
                )
                label.pack(anchor="w", padx=10, pady=5)


    def update_movie_list(self):
    
        for widget in self.movie_frame.winfo_children():
            widget.destroy()
        rows, cols = 3, 6
        for idx, movie in enumerate(self.filtered_movies):
            row, col = divmod(idx, cols)
            poster_image = self.fetch_poster_image(movie["poster"], movie["title"])
            if poster_image:
                button = ctk.CTkButton(
                    self.movie_frame,
                    image=poster_image,
                    text="",
                    fg_color="transparent",
                    hover_color="#333333",
                    command=lambda m=movie: self.show_movie_details(m),
                )
                button.grid(row=row * 2, column=col, padx=5, pady=5)
            title_label = ctk.CTkLabel(self.movie_frame, text=movie["title"], text_color="#FFFFFF")
            title_label.grid(row=row * 2 + 1, column=col, padx=5, pady=(0, 10))

    def fetch_poster_image(self, poster_url, title):
        try:
            image_dir = "movie_posters"
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            valid_filename = "".join(c for c in title if c.isalnum() or c in (" ", ".", "_")).rstrip()
            image_path = os.path.join(image_dir, f"{valid_filename}.jpg")
            
            if os.path.exists(image_path):
                pil_image = Image.open(image_path)
                ctk_image = ctk.CTkImage(pil_image, size=(150, 200))
                return ctk_image
            response = requests.get(poster_url)
            if response.status_code == 200:
                data = response.json()
                if 'Poster' in data and data['Poster'] != 'N/A':
                    poster_image_url = data['Poster']
                    image_response = requests.get(poster_image_url)
                    if image_response.status_code == 200:
                        image_data = io.BytesIO(image_response.content)
                        pil_image = Image.open(image_data)
                        pil_image.save(image_path) 
                        ctk_image = ctk.CTkImage(pil_image, size=(150, 200))
                        return ctk_image
                    else:
                        print(f"Failed to fetch image, status code: {image_response.status_code}")
                else:
                    print("Poster not available for this movie.")
            else:
                print(f"Failed to fetch movie data, status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching poster image: {e}")
        return None

    def dashboard_action(self):
        
        self.search_frame.grid()
        self.sort_filter_frame.grid()
        
       
        self.watchlist_controls_frame.grid_remove()
        
        
        self.filtered_movies = self.movies
        self.update_movie_list()
        

    def watchlist_action(self):
        self.show_watchlist()

    def logout_action(self):
        from login import LoginPage  
        messagebox.showinfo("Logout", "You have been logged out.")
        self.winfo_toplevel().destroy()  
        login_page = LoginPage()  
        login_page.mainloop() 

    def search_movies(self):
        query = self.search_entry.get().strip().lower()
        self.filtered_movies = [movie for movie in self.search_movies_dataset if query in movie["title"].lower()]
        self.update_movie_list()

    def sort_by_year(self):
        sort_order = self.year_var.get()
        if sort_order == "Latest to Oldest":
            self.filtered_movies = sorted(self.filtered_movies, key=lambda x: x["year"], reverse=True)
        elif sort_order == "Oldest to Latest":
            self.filtered_movies = sorted(self.filtered_movies, key=lambda x: x["year"])
        self.update_movie_list()

    def filter_by_genre(self):
        genre = self.genre_var.get()
        if genre == "All":
            self.filtered_movies = self.movies
        else:
            self.filtered_movies = [movie for movie in self.movies if genre.lower() in movie["genre"].lower()]
        self.update_movie_list()

    def filter_by_rating(self):
        
        rating_filter = self.rating_var.get()
        if rating_filter == "All":
            self.filtered_movies = self.movies
        else:
            if rating_filter == "9+":
                self.filtered_movies = [movie for movie in self.movies if float(movie["rating"]) >= 9]
            elif rating_filter == "8-9":
                self.filtered_movies = [movie for movie in self.movies if 8 <= float(movie["rating"]) < 9]
            elif rating_filter == "7-8":
                self.filtered_movies = [movie for movie in self.movies if 7 <= float(movie["rating"]) < 8]
            elif rating_filter == "6-7":
                self.filtered_movies = [movie for movie in self.movies if 6 <= float(movie["rating"]) < 7]
            elif rating_filter == "Below 6":
                self.filtered_movies = [movie for movie in self.movies if float(movie["rating"]) < 6]
        
        self.update_movie_list()

    def reset_filters(self):
        
        self.filtered_movies = self.movies
        self.year_var.set("Sort by year")
        self.genre_var.set("Genre")
        self.rating_var.set("Rating")
        self.search_entry.delete(0, 'end') 
        
        
        self.watchlist_search_entry.delete(0, 'end')
        self.watchlist_sort_var.set("Sort by")
        
        
        self.watchlist_controls_frame.grid_remove()
        
        
        self.search_frame.grid()
        self.sort_filter_frame.grid()
        
        self.update_movie_list()

    import numpy as np

    def generate_report(self, movie):
        """
        Generates a trend report for the given movie using a line graph with a hypothetical trend.
        """
        try:
            # Extract movie details
            movie_name = movie['title']
            release_year = movie['year']
            actual_rating = float(movie['rating'])

            # Generate fake data
            current_year = 2024
            years = list(range(release_year, current_year + 1))
            ratings = np.linspace(5, actual_rating, len(years))  # Hypothetical ratings trend

            # Add some randomness to the trend
            noise = np.random.uniform(-0.5, 0.5, len(ratings))
            ratings = np.clip(ratings + noise, 0, 10)  # Keep ratings between 0 and 10
            ratings[-1] = actual_rating  # Ensure the last point matches the actual rating

            # Plot the trend
            plt.figure(figsize=(10, 6))
            plt.plot(years, ratings, marker='o', linestyle='-', color='b', label=f"Trend for {movie_name}")
            plt.title(f"Rating Trend for {movie_name}", fontsize=16)
            plt.xlabel("Year", fontsize=12)
            plt.ylabel("Rating", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend()

            # Annotate each point
            for i, txt in enumerate(ratings):
                plt.annotate(f"{txt:.1f}", (years[i], ratings[i]), textcoords="offset points", xytext=(0, 5), ha='center')

            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")



    def show_movie_details(self, movie):
        # Existing details window code...

        details_window = ctk.CTkToplevel(self)
        details_window.title(movie["title"])
        details_window.geometry("700x450")
        details_window.configure(fg_color="#1B1B1B")
        details_window.transient(self)
        details_window.grid_rowconfigure(0, weight=1)
        details_window.grid_rowconfigure(1, weight=1)
        details_window.grid_rowconfigure(2, weight=1)
        details_window.grid_rowconfigure(3, weight=1)
        details_window.grid_rowconfigure(4, weight=2)
        details_window.grid_rowconfigure(5, weight=0, minsize=40)
        details_window.grid_columnconfigure(0, weight=1)
        details_window.grid_columnconfigure(1, weight=2)
        details_window.grid_columnconfigure(2, weight=1)

        poster_image = self.fetch_poster_image(movie["poster"], movie["title"])
        if poster_image:
            poster_label = ctk.CTkLabel(details_window, image=poster_image, text="")
            poster_label.image = poster_image 
            poster_label.grid(row=0, column=0, rowspan=4, padx=20, pady=20, sticky="nsew")

        title_label = ctk.CTkLabel(
            details_window,
            text=movie.get('title', 'N/A'),
            font=("Arial", 32, "bold"),
        )
        title_label.grid(row=0, column=1, columnspan=2, sticky="w", padx=10, pady=0)

        year_label = ctk.CTkLabel(
            details_window,
            text=f" {movie.get('year', 'N/A')}",
            font=("Arial", 24),
            text_color="#F1C40F"
        )
        year_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=0)

        details = f"""
        ⭐ Rating: {movie.get('rating', 'N/A')}
        🎬 Director: {movie.get('director', 'N/A')}
        👥 Cast and Crew: {movie.get('cast_and_crew', 'N/A')}
        🎭 Genre: {movie.get('genre', 'N/A')}
        🔞 Age Rating: {movie.get('age_rating', 'N/A')}
        ⏳ Duration: {movie.get('duration', 'N/A')}
        """
        details_label = ctk.CTkLabel(
            details_window,
            text=details,
            font=("Arial", 20),
            text_color="#ECF0F1",
            anchor="w",
            justify="left"
        )
        details_label.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=0)

        button_frame = ctk.CTkFrame(details_window, fg_color="#2E2E2E")
        button_frame.grid(row=4, column=0, columnspan=3, pady=20, padx=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        button_frame.grid_columnconfigure(4, weight=1)

        add_watchlist_button = ctk.CTkButton(
            button_frame,
            text="Add to Watchlist",
            font=("Arial", 16),
            fg_color="#1ABC9C",
            hover_color="#16A085",
            text_color="#FFFFFF",
            command=lambda m=movie: self.add_to_watchlist(m)
        )
        add_watchlist_button.grid(row=0, column=0, padx=5, pady=0, sticky="ew")

        rate_movie_button = ctk.CTkButton(
            button_frame,
            text="Rate Movie",
            font=("Arial", 16),
            fg_color="#F39C12",
            hover_color="#E67E22",
            text_color="#FFFFFF",
            command=lambda m=movie: self.rate_movie(m, details_window)
        )
        rate_movie_button.grid(row=0, column=1, padx=5, pady=0, sticky="ew")

        discussion_button = ctk.CTkButton(
            button_frame,
            text="Discussion",
            font=("Arial", 16),
            fg_color="#3498DB",
            hover_color="#2980B9",
            text_color="#FFFFFF",
            command=lambda m=movie: self.show_discussion(m, details_window)
        )
        discussion_button.grid(row=0, column=2, padx=5, pady=0, sticky="ew")

        generate_report_button = ctk.CTkButton(
            button_frame,
            text="Generate Report",
            font=("Arial", 16),
            fg_color="#9B59B6",
            hover_color="#8E44AD",
            text_color="#FFFFFF",
            command=lambda m=movie: self.generate_report(m)
        )
        generate_report_button.grid(row=0, column=3, padx=5, pady=0, sticky="ew")

        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            font=("Arial", 16),
            fg_color="#E74C3C",
            hover_color="#C0392B",
            text_color="#FFFFFF",
            command=details_window.destroy
        )
        close_button.grid(row=0, column=4, padx=5, pady=0, sticky="ew")

    

    def rate_movie(self, movie,details_window):
        rate_window = ctk.CTkToplevel(self)
        rate_window.title(f"Rate '{movie['title']}'")
        rate_window.geometry("300x200")
        rate_window.configure(fg_color="#2E2E2E")
        rate_window.transient(details_window)
        
        rate_label = ctk.CTkLabel(
            rate_window,
            text=f"Rate '{movie['title']}':",
            font=("Arial", 16, "bold"),
            text_color="#FFFFFF"
        )
        rate_label.pack(pady=20)
        
        rating_var = ctk.DoubleVar(value=5.0)
        rating_slider = ctk.CTkSlider(
            rate_window,
            variable=rating_var,
            from_=0.0,
            to=10.0,
            number_of_steps=10,
            width=200,
            fg_color="#1ABC9C",
            progress_color="#16A085"
        )
        rating_slider.pack(pady=10)
        
        current_rating_label = ctk.CTkLabel(
            rate_window,
            text=f"Current Rating: {rating_var.get():.1f}",
            font=("Arial", 14),
            text_color="#FFFFFF"
        )
        current_rating_label.pack(pady=5)
        
        def update_label(value):
            current_rating_label.configure(text=f"Current Rating: {float(value):.1f}")
        rating_slider.configure(command=update_label)
        
        def submit_rating():
            rating = rating_var.get()
            messagebox.showinfo("Rating Submitted", f"You rated '{movie['title']}' as {rating:.1f}/10.")
            print(f"Movie Rated: {movie['title']} - {rating:.1f}/10")
            rate_window.destroy()
        
        submit_button = ctk.CTkButton(
            rate_window,
            text="Submit",
            font=("Arial", 14),
            fg_color="#1ABC9C",
            hover_color="#16A085",
            text_color="#FFFFFF",
            command=submit_rating
        )
        submit_button.pack(pady=20)
    def add_to_watchlist(self, movie):
        if movie in self.watchlist:
            messagebox.showinfo("Info", f"'{movie['title']}' is already in your watchlist.")
        else:
            self.watchlist.append(movie)
            messagebox.showinfo("Success", f"Added '{movie['title']}' to your watchlist.")
            print(f"Watchlist Updated: {self.watchlist}")
            
    def show_watchlist(self):
        self.watchlist_controls_frame.grid()
        
        
        self.search_frame.grid_remove()
        self.sort_filter_frame.grid_remove()
        
        
        self.filtered_watchlist = self.watchlist.copy()
        self.filtered_movies = self.filtered_watchlist
        self.update_watchlist_movies()


    def remove_from_watchlist(self, movie):
        if movie in self.watchlist:
            self.watchlist.remove(movie)
            messagebox.showinfo("Removed", f"'{movie['title']}' has been removed from your watchlist.")
            print(f"Watchlist Updated: {self.watchlist}")
            
        
            self.filtered_watchlist = self.watchlist.copy()
            self.filtered_movies = self.filtered_watchlist
            self.update_watchlist_movies()
        else:
            messagebox.showinfo("Info", f"'{movie['title']}' is not in your watchlist.")

    def filter_watchlist(self, query):
        
        query = query.strip().lower()
        if not query:
            self.update_watchlist_movies() 
            return
        filtered = [movie for movie in self.watchlist if query in movie["title"].lower()]
        self.filtered_movies = filtered
        self.update_watchlist_movies(filtered=filtered)

    def sort_watchlist(self, criteria):
        
        if criteria == "Title (A-Z)":
            self.filtered_watchlist = sorted(self.watchlist, key=lambda x: x["title"])
        elif criteria == "Title (Z-A)":
            self.filtered_watchlist = sorted(self.watchlist, key=lambda x: x["title"], reverse=True)
        elif criteria == "Year (Newest)":
            self.filtered_watchlist = sorted(self.watchlist, key=lambda x: x["year"], reverse=True)
        elif criteria == "Year (Oldest)":
            self.filtered_watchlist = sorted(self.watchlist, key=lambda x: x["year"])
        self.filtered_movies = self.filtered_watchlist
        self.update_watchlist_movies()

    def update_watchlist_movies(self, filtered=None):
        
        for widget in self.movie_frame.winfo_children():
            widget.destroy()
        
        
        movies_to_display = filtered if filtered is not None else self.filtered_watchlist
        
        if not movies_to_display:
            empty_label = ctk.CTkLabel(
                self.movie_frame,
                text="Your watchlist is empty!",
                font=("Arial", 20),
                text_color="#FFFFFF"
            )
            empty_label.pack(pady=20)
            return
        
        rows, cols = 0, 6
        for idx, movie in enumerate(movies_to_display):
            row, col = divmod(idx, cols)
            poster_image = self.fetch_poster_image(movie["poster"], movie["title"])
            if poster_image:
                button = ctk.CTkButton(
                    self.movie_frame,
                    image=poster_image,
                    text="",
                    fg_color="transparent",
                    hover_color="#333333",
                    command=lambda m=movie: self.show_movie_details(m),
                )
                button.grid(row=row * 3, column=col, padx=5, pady=5)
            title_label = ctk.CTkLabel(self.movie_frame, text=movie["title"], text_color="#FFFFFF")
            title_label.grid(row=row * 3 + 1, column=col, padx=5, pady=(0, 5))
            
            remove_button = ctk.CTkButton(
                self.movie_frame,
                text="Remove",
                font=("Arial", 12),
                fg_color="#E74C3C",
                hover_color="#C0392B",
                text_color="#FFFFFF",
                command=lambda m=movie: self.remove_from_watchlist(m),
            )
            remove_button.grid(row=row * 3 + 2, column=col, padx=5, pady=5)

    def export_watchlist_to_csv(self):
       
        if not self.watchlist:
            messagebox.showinfo("Watchlist", "Your watchlist is empty!")
            return

    
        watchlist_df = pd.DataFrame(self.watchlist)

        
        Visualizer.plot_genre_comparison(watchlist_df)


class LoginRegisterWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login/Register")
        self.geometry("300x400")
        self.configure(fg_color="#1C1C1C")
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        self.username_label = ctk.CTkLabel(self, text="Username:", text_color="#FFFFFF")
        self.username_label.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Enter username")
        self.username_entry.pack(pady=5)

        self.password_label = ctk.CTkLabel(self, text="Password:", text_color="#FFFFFF")
        self.password_label.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Enter password", show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        self.register_button = ctk.CTkButton(self, text="Register", command=self.register)
        self.register_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.parent.users and self.parent.users[username] == password:
            self.parent.current_user = username  # Set the current_user for the app
            messagebox.showinfo("Login", f"Welcome back, {username}!")
            self.destroy()
        else:
            messagebox.showerror("Login", "Invalid username or password.")


    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.parent.users:
            messagebox.showerror("Register", "Username already exists.")
        else:
            self.parent.users[username] = password
            messagebox.showinfo("Register", "Registration successful!")
            self.destroy() 

import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import matplotlib.colors as mcolors

class Visualizer:
    @staticmethod
    def plot_genre_comparison(movies_df):
        genre_data = {}
        for index, row in movies_df.iterrows():
            genres = [g.strip() for g in row["genre"].split(",")]  
            for genre in genres:
                if genre not in genre_data:
                    genre_data[genre] = []
                genre_data[genre].append(row["rating"]) 

        avg_genre_ratings = {genre: sum(ratings) / len(ratings) for genre, ratings in genre_data.items()}
        genres = list(avg_genre_ratings.keys())
        avg_ratings = list(avg_genre_ratings.values())

        
        colors = list(mcolors.TABLEAU_COLORS.values())[:len(genres)]

        plt.figure(figsize=(14, 8))
        bars = plt.bar(genres, avg_ratings, color=colors, edgecolor="black", linewidth=1.5)

        plt.title("Average Ratings by Genre (Watchlist)", fontsize=18, fontweight="bold", color="navy")
        plt.xlabel("Genre", fontsize=14, fontweight="bold", color="darkblue")
        plt.ylabel("Average Rating", fontsize=14, fontweight="bold", color="darkblue")
        plt.xticks(rotation=45, ha="right", fontsize=12, fontweight="bold", color="maroon")
        plt.yticks(fontsize=12, fontweight="bold", color="maroon")
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        
        max_idx = avg_ratings.index(max(avg_ratings))
        min_idx = avg_ratings.index(min(avg_ratings))
        plt.text(
            max_idx, avg_ratings[max_idx] + 0.2, f"Highest\n{avg_ratings[max_idx]:.2f}",
            ha="center", color="green", fontweight="bold"
        )
        plt.text(
            min_idx, avg_ratings[min_idx] + 0.2, f"Lowest\n{avg_ratings[min_idx]:.2f}",
            ha="center", color="red", fontweight="bold"
        )

        cursor = mplcursors.cursor(bars, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            genre = genres[sel.index]
            avg_rating = avg_ratings[sel.index]
            sel.annotation.set(text=f"Genre: {genre}\nAvg Rating: {avg_rating:.2f}", fontsize=10)

        plt.tight_layout()
        plt.show()
           

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = MovieSearchApp()
    app.mainloop()