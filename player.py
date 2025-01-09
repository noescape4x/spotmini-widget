import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import requests
from io import BytesIO
from screeninfo import get_monitors

screen_height = get_monitors()[0].height

# api
CLIENT_ID = "your_spotify_client_id"
CLIENT_SECRET = "your_spotify_client_secret"
REDIRECT_URI = "http://localhost:8080"

# auth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="user-read-currently-playing"))

class SpotifyMiniPlayer:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True) 
        self.root.geometry(f"220x60+10+{screen_height - 80}")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.9)

        self.canvas = tk.Canvas(self.root, width=220, height=60, bg="black", highlightthickness=0)
        self.canvas.pack()
        self.round_rectangle(0, 0, 220, 60, 15, fill="#121212")

        self.frame = tk.Frame(self.root, bg="#121212")
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.album_label = tk.Label(self.frame, bg="#121212")
        self.album_label.pack(side="left", padx=5, pady=5)

        self.song_label = tk.Label(self.frame, text="Fetching song...", font=("Helvetica", 9, "bold"), fg="white", bg="#121212", wraplength=140, justify="left")
        self.song_label.pack(side="left", padx=5)

        self.update_song()

        self.frame.bind("<ButtonPress-1>", self.start_move)
        self.frame.bind("<B1-Motion>", self.do_move)

    def round_rectangle(self, x1, y1, x2, y2, radius=15, **kwargs):
        """ Draw a rounded rectangle on the canvas """
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def get_current_song(self):
        try:
            current_track = sp.currently_playing()
            if current_track and current_track['is_playing']:
                song_name = current_track['item']['name']
                artist_name = current_track['item']['artists'][0]['name']
                album_image_url = current_track['item']['album']['images'][0]['url']
                return f"{song_name}\n{artist_name}", album_image_url
            else:
                return "No song playing", None
        except Exception as e:
            return "Spotify not running", None

    def update_song(self):
        song_info, album_image_url = self.get_current_song()
        self.song_label.config(text=song_info)

        if album_image_url:
            response = requests.get(album_image_url)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((45, 45), Image.LANCZOS)

            mask = Image.new("L", (45, 45), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 45, 45), fill=255)
            img_data.putalpha(mask)

            img = ImageTk.PhotoImage(img_data)
            self.album_label.config(image=img)
            self.album_label.image = img 

        self.root.after(5000, self.update_song)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        self.root.geometry(f"+{event.x_root - self.x}+{event.y_root - self.y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpotifyMiniPlayer(root)
    root.mainloop()
