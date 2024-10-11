# right_frame.py
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging


class RightFrame:
    def __init__(self, parent, main_gui):
        self.parent = parent
        self.main_gui = main_gui  # Reference to the main GUI class

        # Initialize styles
        self.style = ttk.Style()
        self.configure_styles()

        self.create_widgets()
        self.configure_grid()

        # Initialize timer variables
        self.timer_running = False
        self.elapsed_seconds = 0

    def configure_styles(self):
        """Configure custom styles for widgets."""
        # Define a custom style for labels
        self.style.configure('Custom.TLabel', font=("Segoe UI", 10, "bold"), foreground="#333333")

        # Define a custom style for buttons
        self.style.configure('Custom.TButton', font=("Segoe UI", 10))

        # Define a custom style for Comboboxes
        self.style.configure('Custom.TCombobox', font=("Segoe UI", 10))

        # Optionally: Define additional styles if necessary
        # Example: self.style.configure('Custom.TFrame', background="#F0F0F0")

    def create_widgets(self):
        """Create widgets for the right frame."""
        logging.info("Creating widgets for the right frame")

        # Generation Frame
        self.generate_frame = ttk.Frame(self.parent, padding=10, bootstyle="light")
        self.generate_frame.grid(row=0, column=0, sticky='ew', pady=5)
        self.generate_frame.grid_columnconfigure(1, weight=1)

        # Model Selection Label
        model_label = ttk.Label(
            self.generate_frame,
            text="Select Model:",
            style='Custom.TLabel'
        )
        model_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        # Model Selection Combobox
        self.model_var = tk.StringVar(value='gpt-4o-mini')
        self.model_dropdown = ttk.Combobox(
            self.generate_frame,
            textvariable=self.model_var,
            state='readonly',
            values=['gpt-4o-mini', 'gpt-4o'],
            style='Custom.TCombobox'
        )
        self.model_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Character Selection Label
        character_label = ttk.Label(
            self.generate_frame,
            text="Select Character:",
            style='Custom.TLabel'
        )
        character_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')

        # Character Selection Combobox
        self.character_dropdown = ttk.Combobox(
            self.generate_frame,
            state='readonly',
            style='Custom.TCombobox'
        )
        self.character_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Generation Option Variable
        self.generation_option = tk.StringVar(value='continuation')

        # "Continue Dialogue" Button
        self.continue_button = ttk.Button(
            self.generate_frame,
            text="Continue Dialogue",
            bootstyle="success",
            command=lambda: self.handle_generate('continuation'),
            state='disabled',
            style='Custom.TButton'
        )
        self.continue_button.grid(row=2, column=0, padx=5, pady=5, sticky='w')

        # "Get Alternatives" Button
        self.alternatives_button = ttk.Button(
            self.generate_frame,
            text="Get Alternatives",
            bootstyle="success",
            command=lambda: self.handle_generate('alternatives'),
            state='disabled',
            style='Custom.TButton'
        )
        self.alternatives_button.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Timer Label
        self.timer_label = ttk.Label(
            self.generate_frame,
            text="00:00",
            style='Custom.TLabel'
        )
        self.timer_label.grid(row=2, column=2, padx=5, pady=5, sticky='w')

        # Context Frame
        self.context_frame = ttk.Frame(self.parent, padding=10, bootstyle="light")
        self.context_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        self.context_frame.grid_rowconfigure(1, weight=1)
        self.context_frame.grid_columnconfigure(0, weight=1)

        # Preparation Label
        context_label = ttk.Label(
            self.context_frame,
            text="Preparation:",
            style='Custom.TLabel'
        )
        context_label.grid(row=0, column=0, sticky='w', padx=5, pady=(0, 5))

        # Preparation Textbox
        self.preparation_text = tk.Text(
            self.context_frame,
            wrap='word',
            height=6,
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            relief="solid",
            borderwidth=1,
            state='disabled'  # Make it read-only initially
        )
        self.preparation_text.grid(row=1, column=0, sticky='nsew', padx=(0, 5), pady=5)

        # Preparation Scrollbar
        preparation_scroll = ttk.Scrollbar(
            self.context_frame,
            orient='vertical',
            command=self.preparation_text.yview,
            bootstyle="secondary"
        )
        self.preparation_text['yscrollcommand'] = preparation_scroll.set
        preparation_scroll.grid(row=1, column=1, sticky='ns', pady=5)

        # Generated Dialogues Frame
        self.generated_dialogues_frame = ttk.Frame(self.parent, padding=10, bootstyle="light")
        self.generated_dialogues_frame.grid(row=2, column=0, sticky='nsew', pady=5)
        self.generated_dialogues_frame.grid_columnconfigure(0, weight=1)
        # Configure internal rows
        self.generated_dialogues_frame.grid_rowconfigure(1, weight=1)
        self.generated_dialogues_frame.grid_rowconfigure(3, weight=1)
        self.generated_dialogues_frame.grid_rowconfigure(5, weight=1)

        self.generated_text_boxes = []

        # First Generated Dialogue
        label1 = ttk.Label(
            self.generated_dialogues_frame,
            text="Generated Dialogue 1:",
            style='Custom.TLabel'
        )
        label1.grid(row=0, column=0, padx=5, pady=(5, 0), sticky='w')

        text_frame1 = ttk.Frame(self.generated_dialogues_frame, padding=5, bootstyle="light")
        text_frame1.grid(row=1, column=0, sticky='nsew', padx=5, pady=(0, 5))
        text_frame1.grid_rowconfigure(0, weight=1)
        text_frame1.grid_columnconfigure(0, weight=1)

        text_box1 = tk.Text(
            text_frame1,
            wrap='word',
            height=4,
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            relief="solid",
            borderwidth=1,
            state='disabled'  # Make it read-only initially
        )
        text_box1.grid(row=0, column=0, sticky='nsew')

        scrollbar1 = ttk.Scrollbar(
            text_frame1,
            orient='vertical',
            command=text_box1.yview,
            bootstyle="secondary"
        )
        text_box1['yscrollcommand'] = scrollbar1.set
        scrollbar1.grid(row=0, column=1, sticky='ns')

        self.generated_text_boxes.append(text_box1)

        # Autocritic Feedback
        autocritic_label = ttk.Label(
            self.generated_dialogues_frame,
            text="Autocritic Feedback:",
            style='Custom.TLabel'
        )
        autocritic_label.grid(row=2, column=0, sticky='w', padx=5, pady=(5, 0))

        autocritic_frame = ttk.Frame(self.generated_dialogues_frame, padding=5, bootstyle="light")
        autocritic_frame.grid(row=3, column=0, sticky='nsew', padx=5, pady=(0, 5))
        autocritic_frame.grid_rowconfigure(0, weight=1)
        autocritic_frame.grid_columnconfigure(0, weight=1)

        self.autocritic_text = tk.Text(
            autocritic_frame,
            wrap='word',
            height=10,
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            relief="solid",
            borderwidth=1,
            state='disabled'  # Make it read-only initially
        )
        self.autocritic_text.grid(row=0, column=0, sticky='nsew')

        autocritic_scroll = ttk.Scrollbar(
            autocritic_frame,
            orient='vertical',
            command=self.autocritic_text.yview,
            bootstyle="secondary"
        )
        self.autocritic_text['yscrollcommand'] = autocritic_scroll.set
        autocritic_scroll.grid(row=0, column=1, sticky='ns')

        # Second Generated Dialogue
        label2 = ttk.Label(
            self.generated_dialogues_frame,
            text="Generated Dialogue 2:",
            style='Custom.TLabel'
        )
        label2.grid(row=4, column=0, padx=5, pady=(5, 0), sticky='w')

        text_frame2 = ttk.Frame(self.generated_dialogues_frame, padding=5, bootstyle="light")
        text_frame2.grid(row=5, column=0, sticky='nsew', padx=5, pady=(0, 5))
        text_frame2.grid_rowconfigure(0, weight=1)
        text_frame2.grid_columnconfigure(0, weight=1)

        text_box2 = tk.Text(
            text_frame2,
            wrap='word',
            height=4,
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            relief="solid",
            borderwidth=1,
            state='disabled'  # Make it read-only initially
        )
        text_box2.grid(row=0, column=0, sticky='nsew')

        scrollbar2 = ttk.Scrollbar(
            text_frame2,
            orient='vertical',
            command=text_box2.yview,
            bootstyle="secondary"
        )
        text_box2['yscrollcommand'] = scrollbar2.set
        scrollbar2.grid(row=0, column=1, sticky='ns')

        self.generated_text_boxes.append(text_box2)

        # Control Frame
        self.control_frame = ttk.Frame(self.parent, padding=10, bootstyle="light")
        self.control_frame.grid(row=3, column=0, sticky='ew', pady=5)
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)
        self.control_frame.grid_columnconfigure(2, weight=1)

        # Dialogue Choice Variable
        self.dialogue_choice = tk.IntVar(value=1)  # Default to dialogue 1

        # Save Dialogue 1 Button
        self.save_dialogue_1_button = ttk.Button(
            self.control_frame,
            text="Save Dialogue 1",
            bootstyle="success",
            command=lambda: self.save_dialogue(1),
            state='disabled',
            style='Custom.TButton'
        )
        self.save_dialogue_1_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Save Dialogue 2 Button
        self.save_dialogue_2_button = ttk.Button(
            self.control_frame,
            text="Save Dialogue 2",
            bootstyle="success",
            command=lambda: self.save_dialogue(2),
            state='disabled',
            style='Custom.TButton'
        )
        self.save_dialogue_2_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Reroll Dialogue Button
        self.reroll_button = ttk.Button(
            self.control_frame,
            text="Reroll Dialogue",
            bootstyle="warning",
            command=self.reroll_dialogue,
            state='disabled',
            style='Custom.TButton'
        )
        self.reroll_button.grid(row=0, column=2, padx=5, pady=5, sticky='e')

    def configure_grid(self):
        """Configure grid rows and columns for proper resizing."""
        self.parent.grid_rowconfigure(0, weight=0)  # Generation Frame
        self.parent.grid_rowconfigure(1, weight=0)  # Context Frame
        self.parent.grid_rowconfigure(2, weight=1)  # Generated Dialogues Frame
        self.parent.grid_rowconfigure(3, weight=0)  # Control Frame
        self.parent.grid_columnconfigure(0, weight=1)

    # Specific methods for the right frame
    def handle_generate(self, option):
        """Handle actions when generating dialogues."""
        self.generation_option.set(option)
        self.start_timer()  # Start the timer
        self.generate_dialogue()

    def enable_generate_buttons(self):
        """Enable the generate buttons."""
        self.continue_button.config(state='normal')
        self.alternatives_button.config(state='normal')

    def update_character_dropdown(self, characters):
        """Update the character dropdown with a list of names."""
        self.character_dropdown['values'] = characters
        if characters:
            self.character_dropdown.current(0)

    def get_selected_character(self):
        """Return the selected character from the dropdown."""
        return self.character_dropdown.get()

    def get_selected_model(self):
        """Return the selected model from the dropdown."""
        return self.model_var.get()

    def get_generation_option(self):
        """Get the selected generation option."""
        return self.generation_option.get()

    def get_preparation_text(self):
        """Retrieve text from the preparation widget."""
        return self.preparation_text.get("1.0", "end-1c")

    def generate_dialogue(self):
        """Generate the next dialogue line via the controller and stop the timer."""
        logging.info("Generating the next dialogue line in RightFrame")
        self.main_gui.controller.generate_dialogue()

    def on_dialogue_generated(self):
        """Callback method called after dialogue generation."""
        self.stop_timer()

    def display_preparation_text(self, text):
        """Display the preparation text in the textbox."""
        self.preparation_text.config(state='normal')  # Ensure the textbox is editable
        self.preparation_text.delete(1.0, tk.END)
        self.preparation_text.insert(tk.END, text)
        self.preparation_text.config(state='disabled')  # Make it read-only again

    def display_generated_dialogue(self, dialogue_1, dialogue_2):
        """Display the generated dialogues."""
        self.generated_text_boxes[0].config(state='normal')
        self.generated_text_boxes[0].delete(1.0, tk.END)
        self.generated_text_boxes[0].insert(tk.END, dialogue_1)
        self.generated_text_boxes[0].config(state='disabled')

        self.generated_text_boxes[1].config(state='normal')
        self.generated_text_boxes[1].delete(1.0, tk.END)
        self.generated_text_boxes[1].insert(tk.END, dialogue_2)
        self.generated_text_boxes[1].config(state='disabled')

        self.save_dialogue_1_button.config(state='normal')
        self.save_dialogue_2_button.config(state='normal')
        self.reroll_button.config(state='normal')

        # If the generation option is 'alternatives', disable the preparation textbox
        if self.get_generation_option() == 'alternatives':
            self.preparation_text.config(state='disabled')
        else:
            self.preparation_text.config(state='normal')

    def save_dialogue(self, dialogue_number):
        """Save the selected dialogue."""
        logging.info(f"Saving Dialogue {dialogue_number}")
        # Implement the save logic here
        # Example: self.main_gui.controller.save_dialogue(dialogue_number)

    def reroll_dialogue(self):
        """Reroll to generate a new dialogue."""
        logging.info("Rerolling dialogue")
        self.generate_dialogue()

    def display_autocritic_feedback(self, feedback):
        """Display the autocritic feedback in the textbox."""
        self.autocritic_text.config(state='normal')  # Ensure the textbox is editable
        self.autocritic_text.delete(1.0, tk.END)
        self.autocritic_text.insert(tk.END, feedback)
        self.autocritic_text.config(state='disabled')  # Make it read-only again

    # Timer methods
    def start_timer(self):
        """Start the timer to track dialogue generation time."""
        if not self.timer_running:
            self.timer_running = True
            self.elapsed_seconds = 0
            self.update_timer()

    def stop_timer(self):
        """Stop the timer and reset the display."""
        if self.timer_running:
            self.timer_running = False
            self.elapsed_seconds = 0
            self.timer_label.config(text="00:00")

    def update_timer(self):
        """Update the timer label every second."""
        if self.timer_running:
            minutes, seconds = divmod(self.elapsed_seconds, 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            self.elapsed_seconds += 1
            # Schedule the next update after 1 second (1000 milliseconds)
            self.parent.after(1000, self.update_timer)
