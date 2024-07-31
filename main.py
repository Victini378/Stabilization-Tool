import tkinter as tk
from tkinter import Scale, Button, Label, filedialog, messagebox, PhotoImage

import cv2

import threading
import os

from report import generate_report
from stabilizing import local_stabilizer_video, global_stabilizer_video, perspective_stabilizer_video
from video_player import VideoPlayer, VideoControls
from placeholder_entry import PlaceholderEntry

def select_roi():
    video_path = video_path_entry.get()

    if not video_path:
        messagebox.showerror("Error", "Select a video path")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Error", "Error loading video")
        return

    ret, first_frame = cap.read()
    if not ret:
        messagebox.showerror("Error", "Error loading first frame")
        cap.release()
        return

    x,y,w,h = cv2.selectROI("Select a ROI and ENTER", first_frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Select a ROI and ENTER")
    roi_x_entry.delete(0, tk.END)
    roi_x_entry.insert(0, x)
    roi_y_entry.delete(0, tk.END)
    roi_y_entry.insert(0, y)
    roi_width_entry.delete(0, tk.END)
    roi_width_entry.insert(0, w)
    roi_height_entry.delete(0, tk.END)
    roi_height_entry.insert(0, h)

def select_video():
    global video_player

    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi"), ("All files", "*.*")])
    if file_path:
        video_path_entry.delete(0, tk.END)
        video_path_entry.insert(0, file_path)

        directory = os.path.dirname(file_path)
        output_path = os.path.join(directory, "out.avi")
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, output_path)

        for vplayer in vplayers:
            vplayer.load_video(file_path)
        controls.update_slider_range()
    controls.update()

def select_output_path():
    output_path = filedialog.asksaveasfilename(
        defaultextension=".avi",
        filetypes=[("AVI(XVID) files", "*.avi"), ("All files", "*.*")]
    )

    if output_path:
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, output_path)

def start_stabilization():
    video_path = video_path_entry.get()
    output_path = output_path_entry.get()

    if not video_path or not output_path:
        messagebox.showerror("Errore", "Seleziona un video e un percorso di output")
        return

    max_shift_x = int(max_shift_x_entry.get()) if max_shift_x_entry.winfo_ismapped() else 0
    max_shift_y = int(max_shift_y_entry.get()) if max_shift_y_entry.winfo_ismapped() else 0

    try:
        roi_x = int(roi_x_entry.get()) if roi_x_entry.winfo_ismapped() else 0
        roi_y = int(roi_y_entry.get()) if roi_y_entry.winfo_ismapped() else 0
        roi_width = int(roi_width_entry.get()) if roi_width_entry.winfo_ismapped() else 0
        roi_height = int(roi_height_entry.get()) if roi_height_entry.winfo_ismapped() else 0
    except ValueError:
        messagebox.showerror("Errore", "Inserisci le coordinate ROI")
        return

    max_level = int(max_level_entry.get()) if max_level_entry.winfo_ismapped() else 10
    eps = float(eps_entry.get()) if eps_entry.winfo_ismapped() else 0.01
    count = int(count_entry.get()) if count_entry.winfo_ismapped() else 30
    factor = int(factor_entry.get()) if factor_entry.winfo_ismapped() else 4

    stabilization_type = stabilization_type_var.get()
    threading.Thread(target=run_stabilization, args=(video_path, output_path, [max_level, eps, count], [roi_x, roi_y, roi_width, roi_height], [max_shift_x, max_shift_y], stabilization_type, factor)).start()

def run_stabilization(video_path, output_path, lkparams, roi, max_shifts, stabilization_type, factor):
    if stabilization_type == "local":
        local_stabilizer_video(video_path, output_path, lkparams, roi, factor)
    elif stabilization_type == "global":
        global_stabilizer_video(video_path, output_path, lkparams, max_shifts[0], max_shifts[1], factor)
    elif stabilization_type == "perspective":
        perspective_stabilizer_video(video_path, output_path, lkparams, roi, factor)
    
    vplayers[1].load_video(output_path)

def toggle_shift_entries():
    if stabilization_type_var.get() == "global":
        max_shift_x_label.grid(row=5, column=1, columnspan=3, padx=(80,0), pady=5, sticky="W")
        max_shift_x_entry.grid(row=6, column=1, columnspan=3, padx=(75,0), pady=5, sticky="W")
        max_shift_y_label.grid(row=5, column=1, columnspan=3, padx=(0,80), pady=5, sticky="E")
        max_shift_y_entry.grid(row=6, column=1, columnspan=3, padx=(0,75), pady=5, sticky="E")

        roi_select_button.grid_remove()
        roi_x_label.grid_remove()
        roi_x_entry.grid_remove()
        roi_y_label.grid_remove()
        roi_y_entry.grid_remove()
        roi_width_label.grid_remove()
        roi_width_entry.grid_remove()
        roi_height_label.grid_remove()
        roi_height_entry.grid_remove()
    else:
        max_shift_x_label.grid_remove()
        max_shift_x_entry.grid_remove()
        max_shift_y_label.grid_remove()
        max_shift_y_entry.grid_remove()
        
        roi_x_label.grid(row=5, column=1, padx=(0,95), pady=5, sticky="E")
        roi_x_entry.grid(row=6, column=1, padx=(0,80), pady=5, sticky="E")
        roi_y_label.grid(row=5, column=1, padx=(0,20), pady=5, sticky="E")
        roi_y_entry.grid(row=6, column=1, padx=(0,5), pady=5, sticky="E")
        roi_select_button.grid(row=6, column=2, padx=5, pady=5, sticky="WE")
        roi_width_label.grid(row=5, column=3, padx=(5,0), pady=5, sticky="W")
        roi_width_entry.grid(row=6, column=3, padx=(5,0), pady=5, sticky="W")
        roi_height_label.grid(row=5, column=3, padx=(80,0), pady=5, sticky="W")
        roi_height_entry.grid(row=6, column=3, padx=(80,0), pady=5, sticky="W")

def get_entry_data():
    try:
        stabilization_type = stabilization_type_var.get()
        max_shift_x = int(max_shift_x_entry.get()) if max_shift_x_entry.winfo_ismapped() else 0
        max_shift_y = int(max_shift_y_entry.get()) if max_shift_y_entry.winfo_ismapped() else 0
        roi_x = int(roi_x_entry.get()) if roi_x_entry.winfo_ismapped() else 0
        roi_y = int(roi_y_entry.get()) if roi_y_entry.winfo_ismapped() else 0
        roi_width = int(roi_width_entry.get()) if roi_width_entry.winfo_ismapped() else 0
        roi_height = int(roi_height_entry.get()) if roi_height_entry.winfo_ismapped() else 0
        max_level = int(max_level_entry.get()) if max_level_entry.winfo_ismapped() else 10
        eps = float(eps_entry.get()) if eps_entry.winfo_ismapped() else 0.01
        count = int(count_entry.get()) if count_entry.winfo_ismapped() else 30
        factor = int(factor_entry.get()) if factor_entry.winfo_ismapped() else 4
    except ValueError:
        messagebox.showerror("Error", "Please enter all numeric values correctly.")
        return

    return {
        'stabilization_type': stabilization_type,
        'max_shift_x': max_shift_x,
        'max_shift_y': max_shift_y,
        'roi_x': roi_x,
        'roi_y': roi_y,
        'roi_width': roi_width,
        'roi_height': roi_height,
        'max_level': max_level,
        'eps': eps,
        'count': count,
        'factor': factor
    }

if __name__ == "__main__":
    window = tk.Tk()
    window.title("Video Stabilization")
    window.minsize(782,788)
    window.config(padx=5, pady=15)
    window.iconphoto(False, PhotoImage(file="icon.png"))

    vplayers = [VideoPlayer(window), VideoPlayer(window)]
    vplayers[0].grid(row=0, column=0, columnspan=8, padx=5, pady=5, sticky="nw")
    vplayers[1].grid(row=0, column=0, columnspan=8, padx=5, pady=5, sticky="ne")

    controls = VideoControls(window, vplayers)
    controls.grid(row=1, column=0, columnspan=8, padx=5, pady=5, sticky="ew")

    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)
    window.grid_columnconfigure(3, weight=1)
    window.grid_columnconfigure(4, weight=1)
    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(6, weight=1)

    tk.Label(window, text="Video Path:").grid(row=2, column=0, padx=10, pady=5, sticky="W")
    video_path_entry = tk.Entry(window)
    video_path_entry.grid(row=2, column=0, columnspan=4, padx=(90,5), pady=5, sticky="WE")
    tk.Button(window, text="Browse", command=select_video).grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)

    tk.Label(window, text="Output Path:").grid(row=3, column=0, padx=10, pady=5, sticky="W")
    output_path_entry = tk.Entry(window)
    output_path_entry.grid(row=3, column=0, columnspan=4, padx=(90,5), pady=5, sticky="WE")
    tk.Button(window, text="Browse", command=select_output_path).grid(row=3, column=4, padx=5, pady=5, sticky=tk.W)

    max_shift_x_label = tk.Label(window, text="Max Shift X")
    max_shift_x_entry = tk.Scale(window, from_=-200, to=200, orient=tk.HORIZONTAL)
    max_shift_y_label = tk.Label(window, text="Max Shift Y")
    max_shift_y_entry = tk.Scale(window, from_=-200, to=200, orient=tk.HORIZONTAL)

    roi_select_button = tk.Button(window, text="Select ROI", command=select_roi)
    roi_x_label = tk.Label(window, text="ROI X")
    roi_x_entry = tk.Entry(window, width=10)
    roi_y_label = tk.Label(window, text="ROI Y")
    roi_y_entry = tk.Entry(window, width=10)
    roi_width_label = tk.Label(window, text="ROI Width")
    roi_width_entry = tk.Entry(window, width=10)
    roi_height_label = tk.Label(window, text="ROI Height")
    roi_height_entry = tk.Entry(window, width=10)

    stabilization_type_var = tk.StringVar(value="local")
    tk.Radiobutton(window, text="Local Stabilization", variable=stabilization_type_var, value="local", command=toggle_shift_entries).grid(row=4, column=1, padx=5, pady=5, sticky="WE")
    tk.Radiobutton(window, text="Global Stabilization", variable=stabilization_type_var, value="global", command=toggle_shift_entries).grid(row=4, column=2, padx=5, pady=5, sticky="WE")
    tk.Radiobutton(window, text="Perspective Stabilization", variable=stabilization_type_var, value="perspective", command=toggle_shift_entries).grid(row=4, column=3, padx=5, pady=5, sticky="WE")

    toggle_shift_entries()

    tk.Label(window, text="Max Level").grid(row=7, column=1, padx=5, pady=5, sticky="WE")
    max_level_entry = PlaceholderEntry(window, width=10, placeholder=10)
    max_level_entry.grid(row=8, column=1, padx=5, pady=5)
    tk.Label(window, text="EPS").grid(row=7, column=2, padx=5, pady=5, sticky="WE")
    eps_entry = PlaceholderEntry(window, width=10, placeholder=0.01)
    eps_entry.grid(row=8, column=2, padx=5, pady=5)
    tk.Label(window, text="COUNT").grid(row=7, column=3, padx=5, pady=5, sticky="WE")
    count_entry = PlaceholderEntry(window, width=10, placeholder=30)
    count_entry.grid(row=8, column=3, padx=5, pady=5)

    tk.Label(window, text="Factor").grid(row=9, column=2, padx=5, pady=5, sticky="WE")
    factor_entry = PlaceholderEntry(window, width=10, placeholder=4)
    factor_entry.grid(row=10, column=2, padx=5, pady=5)

    tk.Button(window, text="Start Stabilization", command=start_stabilization).grid(row=11, column=2, padx=5, pady=15)
    tk.Button(window, text="Generate Report", command=lambda: generate_report(get_entry_data())).grid(row=11, column=0, padx=5, pady=15)

    window.mainloop()