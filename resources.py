# resources.py
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import os
import pandas as pd

shared_resources = {}

def load_movies(file_path):
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
                lambda title: f"http://www.omdbapi.com/?t={title}&apikey={api_key}")

            return df.to_dict(orient="records")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load movie data: {str(e)}")

def load_images():
    shared_resources["logo_image"] = CTkImage(Image.open("./logo.png"), size=(100, 100))
    shared_resources["movies"] = load_movies("moviedata.csv")
