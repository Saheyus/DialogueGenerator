import tkinter as tk
from gui import AlteirExtractorGUI

def main():
    root = tk.Tk()
    app = AlteirExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
