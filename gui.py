# gui.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import os

# Import the controller
from controller import AlteirController
from left_frame import LeftFrame
from right_frame import RightFrame


class AlteirExtractorGUI:
    def __init__(self, master):
        self.master = master  # Utiliser la fenêtre principale passée en paramètre
        self.master.title("Alteir Dialogue Extractor")
        self.master.geometry("1400x900")

        # Configuration des styles globaux (optionnel)
        self.style = ttk.Style()
        self.style.configure('TFrame', padding=10)
        self.style.configure('TLabel', font=("Segoe UI", 10, "bold"))
        self.style.configure('TButton', font=("Segoe UI", 10))
        self.style.configure('TCombobox', font=("Segoe UI", 10))

        # Configuration des thèmes (si nécessaire)
        # Par exemple, pour personnaliser davantage les styles
        # self.style.configure('Custom.TFrame', background="#f0f0f0")

        # Set up logging level based on environment variable
        logging_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(level=getattr(logging, logging_level, 'INFO'), format='%(levelname)s: %(message)s')

        # Default XML file path
        self.default_xml_path = r"F:\Unity\Alteir\Alteir\Assets\Dialogs\Alteir.xml"

        # Build the GUI
        self.create_widgets()

        # Initialize the controller after widgets are created
        self.controller = AlteirController(self)

        # Set default XML file path and load on start
        self.xml_file_path = self.default_xml_path
        self.output_file_path = "dialogues_exported.json"
        logging.info("Loading XML file at startup")
        self.load_xml()  # Load the XML file on startup

    def create_widgets(self):
        """Create all the GUI widgets."""
        logging.info("Creating widgets")
        self.create_menu()
        self.configure_grid()
        self.create_main_frames()
        # Create instances of LeftFrame and RightFrame
        self.left_frame_ui = LeftFrame(self.left_frame, self)
        self.right_frame_ui = RightFrame(self.right_frame, self)

    def create_menu(self):
        """Create the menu bar."""
        logging.info("Creating menu bar")
        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Set XML File Path", command=self.browse_xml_file)
        file_menu.add_command(label="Set Output JSON File Path", command=self.browse_output_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

    def configure_grid(self):
        """Configure the main grid layout."""
        logging.info("Configuring grid layout")
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

    def create_main_frames(self):
        """Create main frames for layout."""
        logging.info("Creating main frames")
        self.main_frame = ttk.Frame(self.master, bootstyle="light")
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Left frame for dialogue list and fragment text
        self.left_frame = ttk.Frame(self.main_frame, bootstyle="light")
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Right frame for generated dialogues and controls
        self.right_frame = ttk.Frame(self.main_frame, bootstyle="light")
        self.right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

    # GUI Methods that interact with the controller

    def browse_xml_file(self):
        """Open a file dialog to browse for an XML file."""
        logging.info("Browsing for XML file")
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            self.xml_file_path = file_path
            self.load_xml()

    def browse_output_file(self):
        """Open a file dialog to browse for an output JSON file."""
        logging.info("Browsing for output JSON file")
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            self.output_file_path = file_path

    def load_xml(self):
        """Load the XML file using the controller."""
        logging.info("Loading XML file")
        self.controller.load_xml()

    # Other helper methods

    def display_message(self, title, message):
        """Display an information message box."""
        logging.info(f"Displaying message - Title: {title}, Message: {message}")
        messagebox.showinfo(title, message)

    def display_error(self, title, message):
        """Display an error message box."""
        logging.error(f"Displaying error - Title: {title}, Message: {message}")
        messagebox.showerror(title, message)

    def get_xml_file_path(self):
        """Get the XML file path."""
        xml_path = getattr(self, 'xml_file_path', self.default_xml_path)
        logging.info(f"XML file path: {xml_path}")
        return xml_path

    def get_output_file_path(self):
        """Get the output JSON file path."""
        output_path = getattr(self, 'output_file_path', "dialogues_exported.json")
        logging.info(f"Output file path: {output_path}")
        return output_path


if __name__ == "__main__":
    root = ttk.Window(themename="superhero")  # Choose a modern theme like "superhero"
    app = AlteirExtractorGUI(root)
    root.mainloop()
