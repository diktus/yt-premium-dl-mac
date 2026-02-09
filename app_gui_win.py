import tkinter as tk
from tkinter import scrolledtext

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Premium Downloader")
        self.root.geometry("900x1050")  # Updated window size

        # Configure rows to fit all elements
        self.root.grid_rowconfigure(0, weight=1)  # Download button
        self.root.grid_rowconfigure(1, weight=5)  # Scrollable log area

        self.download_button = tk.Button(self.root, text="Download", command=self.download)
        self.download_button.grid(row=0, sticky='ew', padx=10, pady=10)

        # Scrollable log area
        self.log_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.log_area.grid(row=1, sticky='nsew', padx=10, pady=10)

    def download(self):
        # download functionality here
        pass

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()