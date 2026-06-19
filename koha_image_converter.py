#!/usr/bin/env python3

import os
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox

from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD


# ---------------- APP SETTINGS ---------------- #

APP_NAME = "Koha Bulk Image ZIP Generator"

selected_files = []


# ---------------- IMAGE PROCESS ---------------- #

def compress_image(input_path, output_path):

    img = Image.open(input_path)
    img = img.convert("RGB")

    img = img.resize(
        (int(width_entry.get()), int(height_entry.get())),
        Image.LANCZOS
    )

    quality = 95

    img.save(output_path, "JPEG", quality=quality, optimize=True)

    target_kb = int(size_entry.get())

    while (
        os.path.getsize(output_path) > target_kb * 1024
        and quality > 25
    ):
        quality -= 5
        img.save(output_path, "JPEG", quality=quality, optimize=True)


# ---------------- FILE SELECTION ---------------- #

def select_folder():

    global selected_files

    folder = filedialog.askdirectory(
        initialdir=str(Path.home())
    )

    if not folder:
        return

    selected_files = []

    for f in os.listdir(folder):
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            selected_files.append(os.path.join(folder, f))

    update_list()


def select_files():

    global selected_files

    files = filedialog.askopenfilenames(
        initialdir=str(Path.home() / "Pictures"),
        filetypes=[("Images", "*.jpg *.jpeg *.png *.gif")]
    )

    selected_files = list(files)
    update_list()


def update_list():

    file_box.delete("1.0", "end")

    for f in selected_files:
        file_box.insert("end", os.path.basename(f) + "\n")

    status_label.configure(
        text=f"{len(selected_files)} files selected"
    )


# ---------------- DRAG & DROP ---------------- #

def drop(event):

    global selected_files

    files = root.tk.splitlist(event.data)

    selected_files = list(files)
    update_list()


# ---------------- ZIP GENERATION ---------------- #

def generate_zip():

    if not selected_files:
        messagebox.showerror("Error", "No images selected")
        return

    output_zip = filedialog.asksaveasfilename(
        defaultextension=".zip",
        initialfile=f"koha-bulk-images-{datetime.now().strftime('%Y-%m-%d')}.zip"
    )

    if not output_zip:
        return

    progress.set(0)
    status_label.configure(text="Processing...")

    root.update()

    with tempfile.TemporaryDirectory() as tmp:

        idfile = os.path.join(tmp, "IDLINK.TXT")

        with open(idfile, "w") as f:

            total = len(selected_files)

            for i, img_file in enumerate(selected_files):

                name = os.path.splitext(os.path.basename(img_file))[0]
                out_img = os.path.join(tmp, f"{name}.jpeg")

                compress_image(img_file, out_img)

                f.write(f"{name}\t{name}.jpeg\n")

                progress.set((i + 1) / total)
                root.update()

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z:

            for f in os.listdir(tmp):
                z.write(os.path.join(tmp, f), f)

    progress.set(1)
    status_label.configure(text="Done!")

    messagebox.showinfo("Success", f"ZIP created:\n{output_zip}")


# ---------------- ABOUT ---------------- #

def about():

    messagebox.showinfo(
        "About",
        f"{APP_NAME}\n\n"
        "Version 2.2\n\n"
        "Developer:\n"
        "Mahesh Palamuttath\n\n"
        "Email: maheshpalamuttath@gmail.com\n"
        "Mobile: (+91 9567 664 972)\n\n"
        "Tool for generating Koha-ready bulk image ZIP packages."
    )


# ---------------- UI ---------------- #

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = TkinterDnD.Tk()
root.title(APP_NAME)

root.geometry("950x650")
root.minsize(850, 550)


# TITLE
title = ctk.CTkLabel(
    root,
    text=APP_NAME,
    font=("Ubuntu", 24, "bold")
)
title.pack(pady=10)


# SETTINGS
settings_frame = ctk.CTkFrame(root)
settings_frame.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(settings_frame, text="Width").pack(side="left", padx=5)
width_entry = ctk.CTkEntry(settings_frame, width=60)
width_entry.insert(0, "140")
width_entry.pack(side="left")

ctk.CTkLabel(settings_frame, text="Height").pack(side="left", padx=5)
height_entry = ctk.CTkEntry(settings_frame, width=60)
height_entry.insert(0, "158")
height_entry.pack(side="left")

ctk.CTkLabel(settings_frame, text="KB Limit").pack(side="left", padx=5)
size_entry = ctk.CTkEntry(settings_frame, width=60)
size_entry.insert(0, "20")
size_entry.pack(side="left")


# BUTTONS
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=10)

ctk.CTkButton(btn_frame, text="📁 Select Folder", command=select_folder).pack(side="left", padx=10)
ctk.CTkButton(btn_frame, text="🖼 Select Files", command=select_files).pack(side="left", padx=10)
ctk.CTkButton(btn_frame, text="⚡ Generate ZIP", command=generate_zip).pack(side="left", padx=10)
ctk.CTkButton(btn_frame, text="ℹ About", command=about).pack(side="left", padx=10)


# FILE LIST
file_box = ctk.CTkTextbox(root, height=300)
file_box.pack(fill="both", expand=True, padx=20, pady=10)

file_box.insert("end", "Drop files here or use buttons above...\n")

file_box.drop_target_register(DND_FILES)
file_box.dnd_bind("<<Drop>>", drop)


# PROGRESS
progress = ctk.CTkProgressBar(root)
progress.pack(fill="x", padx=20, pady=10)
progress.set(0)


# STATUS
status_label = ctk.CTkLabel(root, text="Ready")
status_label.pack(pady=5)


root.mainloop()
