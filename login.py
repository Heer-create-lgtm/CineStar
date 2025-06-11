import customtkinter as ctk
from tkinter import messagebox as tkmb
from PIL import Image
from customtkinter import CTkImage
import sqlite3
import resources
from maingui2 import MovieSearchApp 



ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue") 

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def register_user(username, password):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def validate_login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

class BasePage(ctk.CTk):
    def __init__(self, title, parent=None):
        super().__init__()
        self.parent = parent
        self.logo_image = resources.shared_resources["logo_image"]
        self.title(title)
        self.geometry("800x600")
        self.resizable(False, False)

    def add_logo(self):
        self.logo_label = ctk.CTkLabel(self, image=self.logo_image, text="")
        self.logo_label.place(relx=0.5, rely=0.15, anchor="center")

class LoginPage(BasePage):
    def __init__(self):
        resources.load_images()
        super().__init__("CineStar+ Login Page")
        self.add_logo()
        self.add_login_form()

    def add_login_form(self):

        self.welcome_label = ctk.CTkLabel(self, text="Welcome to CineStar+", 
                                          font=ctk.CTkFont(size=24, weight="bold"), 
                                          text_color="white")
        self.welcome_label.place(relx=0.5, rely=0.3, anchor="center")


        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.username_entry.place(relx=0.5, rely=0.45, anchor="center")


        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.password_entry.place(relx=0.5, rely=0.52, anchor="center")


        self.login_button = ctk.CTkButton(self, text="Login", command=self.login_action, width=200,
                                          fg_color="#5865F2", hover_color="#4e5cd2", text_color="white")
        self.login_button.place(relx=0.5, rely=0.6, anchor="center")


        self.register_button = ctk.CTkButton(self, text="Register an account",
                                             font=ctk.CTkFont(size=10),
                                             fg_color="transparent", hover_color="#a8d5e5",
                                             text_color="#5865F2", command=self.register_action)
        self.register_button.place(relx=0.5, rely=0.7, anchor="center")

    def login_action(self):
        from maingui2 import MovieSearchApp 
        username = self.username_entry.get()
        password = self.password_entry.get()

        if validate_login(username, password):
            self.destroy()
            movie_app = MovieSearchApp(username)  
            movie_app.mainloop()
        else:
            tkmb.showerror("Login Failed", "Invalid username or password.")






    def register_action(self):
        self.destroy()  
        register_page = RegisterPage(self)
        register_page.mainloop()

class RegisterPage(BasePage):
    def __init__(self, parent):
        resources.load_images()
        super().__init__("CineStar+ Register Page", parent)
        self.add_logo()
        self.add_register_form()

    def add_register_form(self):

        self.welcome_label = ctk.CTkLabel(self, text="Register an Account", 
                                          font=ctk.CTkFont(size=24, weight="bold"), 
                                          text_color="white")
        self.welcome_label.place(relx=0.5, rely=0.27, anchor="center")


        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.username_entry.place(relx=0.5, rely=0.35, anchor="center")


        self.password_entry = ctk.CTkEntry(self, placeholder_text="Set Password", show="*", width=250)
        self.password_entry.place(relx=0.5, rely=0.42, anchor="center")


        self.confirm_password_entry = ctk.CTkEntry(self, placeholder_text="Confirm Password", show="*", width=250)
        self.confirm_password_entry.place(relx=0.5, rely=0.49, anchor="center")


        self.register_button = ctk.CTkButton(self, text="Register", command=self.register_action, width=200,
                                             fg_color="#5865F2", hover_color="#4e5cd2", text_color="white")
        self.register_button.place(relx=0.5, rely=0.58, anchor="center")

        self.back_button = ctk.CTkButton(self, text="Back to Login",
                                         font=ctk.CTkFont(size=10),
                                         fg_color="transparent", hover_color="#c5dfe8",
                                         text_color="#5865F2", command=self.back_to_login)
        self.back_button.place(relx=0.5, rely=0.65, anchor="center")

    def register_action(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not all([username, password, confirm_password]):
            tkmb.showwarning("Invalid Input", "All fields are required!")
            return

        if password != confirm_password:
            tkmb.showerror("Password Mismatch", "Passwords do not match!")
            return

        if register_user(username, password):
            tkmb.showinfo("Registration Successful", f"Welcome, {username}! Your account has been created.")
            self.back_to_login()
        else:
            tkmb.showerror("Registration Failed", "Username already exists!")

    def back_to_login(self):
        self.destroy()
        login_page = LoginPage()
        login_page.mainloop()


init_db()


if __name__ == "__main__":
    app = LoginPage()  
    app.mainloop()

