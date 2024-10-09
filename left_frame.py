# left_frame.py
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging


class LeftFrame:
    def __init__(self, parent, main_gui):
        self.parent = parent
        self.main_gui = main_gui  # Reference to the main GUI class
        self.dialogue_ids = {}  # Stores dialogue display text to ID mapping
        self.fragment_ids = {}  # Stores fragment display text to ID mapping
        self.selected_id = None  # Currently selected dialogue or fragment ID

        self.create_widgets()
        self.configure_grid()

    def create_widgets(self):
        """Create widgets for the left frame."""
        logging.info("Creating left frame widgets")

        # Dialogue Listbox with Scrollbar
        self.listbox_frame = ttk.Frame(self.parent, padding=5, bootstyle="light")
        self.listbox_frame.grid(row=0, column=0, sticky='nsew')

        self.listbox = tk.Listbox(self.listbox_frame, font=("Segoe UI", 10))
        self.listbox.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)

        self.listbox_scrollbar = ttk.Scrollbar(
            self.listbox_frame, orient='vertical', command=self.listbox.yview, bootstyle="secondary"
        )
        self.listbox['yscrollcommand'] = self.listbox_scrollbar.set
        self.listbox_scrollbar.grid(row=0, column=1, sticky='ns', pady=5)

        self.listbox_frame.grid_rowconfigure(0, weight=1)
        self.listbox_frame.grid_columnconfigure(0, weight=1)

        # Fragment Text Box with Scrollbar
        self.fragment_text_frame = ttk.Frame(self.parent, padding=5, bootstyle="light")
        self.fragment_text_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        self.fragment_text_frame.grid_rowconfigure(1, weight=1)
        self.fragment_text_frame.grid_columnconfigure(0, weight=1)

        fragment_label = ttk.Label(
            self.fragment_text_frame, text="Fragment Text:", font=("Segoe UI", 10, "bold")
        )
        fragment_label.grid(row=0, column=0, sticky='w', pady=(0, 5))

        self.fragment_text_box = tk.Text(
            self.fragment_text_frame, wrap='word', height=20, font=("Segoe UI", 10), bg="#F8F8F8", relief="flat"
        )
        self.fragment_text_box.grid(row=1, column=0, sticky='nsew', padx=(0, 5), pady=5)

        fragment_scrollbar = ttk.Scrollbar(
            self.fragment_text_frame, orient='vertical', command=self.fragment_text_box.yview, bootstyle="secondary"
        )
        self.fragment_text_box['yscrollcommand'] = fragment_scrollbar.set
        fragment_scrollbar.grid(row=1, column=1, sticky='ns', pady=5)

        # Instruction Frame moved to the bottom
        self.instruction_frame = ttk.Frame(self.parent, padding=5, bootstyle="light")
        self.instruction_frame.grid(row=2, column=0, sticky='ew', pady=5)
        self.instruction_frame.grid_rowconfigure(1, weight=1)
        self.instruction_frame.grid_columnconfigure(0, weight=1)

        instruction_label = ttk.Label(
            self.instruction_frame, text="Custom Instruction:", font=("Segoe UI", 10, "bold")
        )
        instruction_label.grid(row=0, column=0, sticky='w', padx=5, pady=(0, 5))

        # Changed Entry to Text widget with 4 lines
        self.custom_instruction_text = tk.Text(
            self.instruction_frame, wrap='word', height=4, font=("Segoe UI", 10), bg="#F8F8F8", relief="flat"
        )
        self.custom_instruction_text.grid(row=1, column=0, sticky='nsew', padx=(0, 5), pady=5)

        # Optional scrollbar for the instruction text
        instruction_scrollbar = ttk.Scrollbar(
            self.instruction_frame, orient='vertical', command=self.custom_instruction_text.yview, bootstyle="secondary"
        )
        self.custom_instruction_text['yscrollcommand'] = instruction_scrollbar.set
        instruction_scrollbar.grid(row=1, column=1, sticky='ns', pady=5)

    def configure_grid(self):
        """Configure grid rows and columns for proper resizing."""
        self.parent.grid_rowconfigure(0, weight=1)  # Listbox frame
        self.parent.grid_rowconfigure(1, weight=2)  # Fragment text frame
        self.parent.grid_rowconfigure(2, weight=1)  # Instruction frame
        self.parent.grid_columnconfigure(0, weight=1)

    # Methods specific to left_frame
    def on_listbox_select(self, event):
        """Handle listbox selection events."""
        logging.info("Listbox item selected in LeftFrame")
        display_text = self.get_listbox_selection()
        if display_text:
            if display_text.startswith("Dialogue ID:"):
                self.selected_id = self.dialogue_ids.get(display_text)
            elif display_text.startswith("Fragment ID:"):
                self.selected_id = self.fragment_ids.get(display_text)
            else:
                self.selected_id = None

            if self.selected_id:
                # Display the fragment text
                fragment_text = self.main_gui.controller.get_fragment_text(self.selected_id)
                self.display_fragment_text(fragment_text)
                # Start the extraction process
                self.main_gui.controller.selected_id = self.selected_id  # Update selected ID in controller
                self.main_gui.controller.extract()
        else:
            logging.info("No selection in listbox")

    def display_fragment_text(self, fragment_text):
        """Display the selected fragment text in the text box."""
        self.fragment_text_box.delete(1.0, tk.END)
        self.fragment_text_box.insert(tk.END, fragment_text)

    def get_listbox_selection(self):
        """Get the current selection from the listbox."""
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            display_text = self.listbox.get(index)
            logging.info(f"Listbox selection: {display_text}")
            return display_text
        logging.info("No selection in listbox")
        return None

    def get_custom_instruction(self):
        """Retrieve the text from the custom instruction text widget."""
        return self.custom_instruction_text.get("1.0", "end-1c")

    def insert_into_listbox(self, index, text):
        """Insert text into the listbox at the specified index."""
        self.listbox.insert(index, text)

    def clear_listbox(self):
        """Clear the listbox."""
        self.listbox.delete(0, tk.END)

    def add_dialogue_id(self, display_text, dialogue_id):
        """Add a dialogue ID to the dialogue IDs dictionary."""
        self.dialogue_ids[display_text] = dialogue_id

    def clear_dialogue_ids(self):
        """Clear the dialogue IDs dictionary."""
        self.dialogue_ids.clear()

    def add_fragment_id(self, display_text, fragment_id):
        """Add a fragment ID to the fragment IDs dictionary."""
        self.fragment_ids[display_text] = fragment_id

    def clear_fragment_ids(self):
        """Clear the fragment IDs dictionary."""
        self.fragment_ids.clear()
