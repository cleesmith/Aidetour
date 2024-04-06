import customtkinter as ctk
from PIL import Image

def show_alert():
    """
    Show a custom alert dialog with an image.
    """
    alert_window = ctk.CTkToplevel(window)
    alert_window.title("Alert")
    alert_window.geometry("400x300")

    alert_label = ctk.CTkLabel(alert_window, text="This is an informational alert box.")
    alert_label.pack(pady=20)

    image = ctk.CTkImage(Image.open("Aidetour.png"), size=(200, 200))
    image_label = ctk.CTkLabel(alert_window, image=image, text="")
    image_label.pack(pady=10)

    close_button = ctk.CTkButton(alert_window, text="Close", command=alert_window.destroy)
    close_button.pack(pady=20)

def main():
    global window
    window = ctk.CTk()
    window.title("Main Window")
    window.geometry("600x400")

    ctk.set_appearance_mode("dark")  # Set the appearance mode to dark

    alert_button = ctk.CTkButton(window, text="Show Alert", command=show_alert)
    alert_button.pack(pady=20)

    # Here you can add more of your main application functionality

    window.mainloop()

if __name__ == "__main__":
    main()