import tkinter as tk
from tkinter import Canvas, Scale, Button, Label

import cv2
from PIL import Image, ImageTk

import time
import threading

class VideoPlayer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = Canvas(self, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.video_source = None
        self.vid = None
        self.fps = 0
        self.frame_count = 0
        self.duration = 0
        self.frame_interval = 0
        self.current_frame = 0

        self.is_playing = False

        self.mutex = threading.Lock()

    def load_video(self, video_source):
        self.video_source = video_source
        self.vid = cv2.VideoCapture(video_source)
        self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))
        self.frame_count = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps
        self.frame_interval = int(1000 // self.fps)
        self.update_frame()

    def update_frame(self):
        if self.vid and self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                start_time = time.time()

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image = image.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), Image.BOX)
                photo = ImageTk.PhotoImage(image)

                self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                self.canvas.image = photo
                self.current_frame = int(self.vid.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                elapsed_time = (time.time() - start_time) * 1000

                return elapsed_time
        return -1

    def seek(self, frame_number):
        if self.vid and self.vid.isOpened():
            with self.mutex:
                self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            if not self.is_playing:
                self.update_frame()

    def play(self):
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def release(self):
        if self.vid:
            self.vid.release()


class VideoControls(tk.Frame):
    def __init__(self, parent, players):
        super().__init__(parent)
        self.players = players

        self.is_playing = False

        self.slider = Scale(self, from_=0, to=1, orient=tk.HORIZONTAL, command=self.seek)
        self.slider.pack(fill=tk.X, padx=10, pady=5)

        self.play_button = Button(self, text="Play", command=self.toggle_play)
        self.play_button.pack(pady=5)

        self.time_label = Label(self, text="00:00 / 00:00")
        self.time_label.pack(pady=5)

        self.update_slider_range()

    def update_slider_range(self):
        if self.players:
            max_frames = min(player.frame_count for player in self.players)
            self.slider.config(to=max_frames - 1)

    def update(self):
        if self.players:
            current_frame = min(player.current_frame for player in self.players)

            original_command = self.slider.cget("command")
            self.slider.config(command=self.unseek)
            self.slider.set(current_frame)
            self.slider.config(command=original_command)

            self.update_time_label()

    def update_time_label(self):
        if self.players:
            current_time = min(player.current_frame / player.fps for player in self.players)
            duration = min(player.duration for player in self.players)
            elapsed_time_str = self.format_time(current_time)
            duration_str = self.format_time(duration)
            self.time_label.config(text=f"{elapsed_time_str} / {duration_str}")

    def toggle_play(self):
        if any(player.is_playing for player in self.players):
            for player in self.players:
                player.pause()
            self.play_button.config(text="Play")
            self.is_playing = False
            self.slider.config(command=self.seek)
        else:
            for player in self.players:
                player.play()
            self.play_button.config(text="Pause")
            self.is_playing = True
            self.slider.config(command=self.unseek)
            threading.Thread(target=self.play_videos).start()

    def play_videos(self):
        while self.is_playing:
            intervals = [player.update_frame() for player in self.players]
            if any(interval == -1 for interval in intervals):
                self.toggle_play()
                break
            self.update()
            time.sleep(max(0, self.players[0].frame_interval - sum(intervals))/1000)

    def seek(self, value):
        frame_number = int(value)
        for player in self.players:
            player.seek(frame_number)

    def unseek(self, value):
        pass

    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02}:{seconds:02}"