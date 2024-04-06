import sys
import tkinter as tk
from PIL import Image, ImageTk

def show_splash(image_path, message, duration=3000):
    root = tk.Tk()
    root.overrideredirect(True)

    img = Image.open(image_path)
    imgTk = ImageTk.PhotoImage(img)
    canvas = tk.Canvas(root, height=img.height + 140, width=img.width)  # Adjusted for message space
    canvas.pack()
    canvas.create_image(img.width / 2, img.height / 2, image=imgTk)

    # Display a message below the image
    # canvas.create_text(img.width / 2, img.height + 100, text=message, fill="white")
    canvas.create_text(img.width / 2, img.height + 60, text=message, fill="white", font=("Comic Sans MS", 30))

    # Center the splash screen
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (img.width / 2)
    y = (hs / 2) - ((img.height + 60) / 2)  # Adjusted for message space
    root.geometry('+%d+%d' % (x, y))

    # Show the splash screen for a certain duration then destroy
    root.after(duration, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    image_path = sys.argv[1]
    message =  sys.argv[2]
    show_splash(image_path, message)

