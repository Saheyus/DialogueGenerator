# right_frame.py
import tkinter as tk  # Import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging


class RightFrame:
    def __init__(self, parent, main_gui):
        self.parent = parent
        self.main_gui = main_gui  # Référence à la classe GUI principale

        # Initialiser les styles
        self.style = ttk.Style()
        self.configure_styles()

        self.create_widgets()
        self.configure_grid()

    def configure_styles(self):
        """Configurer les styles personnalisés pour les widgets."""
        # Définir un style personnalisé pour les labels
        self.style.configure('Custom.TLabel', font=("Segoe UI", 10, "bold"), foreground="#333333")
        
        # Définir un style personnalisé pour les boutons
        self.style.configure('Custom.TButton', font=("Segoe UI", 10))
        
        # Définir un style personnalisé pour les Combobox
        self.style.configure('Custom.TCombobox', font=("Segoe UI", 10))
        
        # Optionnel: Définir des styles supplémentaires si nécessaire
        # Exemple: self.style.configure('Custom.TFrame', background="#F0F0F0")

    def create_widgets(self):
        """Créer les widgets pour le cadre droit."""
        logging.info("Création des widgets du cadre droit")

        # Frame Génération
        self.generate_frame = ttk.Frame(self.parent, padding=10, bootstyle="light")
        self.generate_frame.grid(row=0, column=0, sticky='ew', pady=5)
        self.generate_frame.grid_columnconfigure(1, weight=1)

        # Label Sélection du Modèle
        model_label = ttk.Label(
            self.generate_frame, 
            text="Sélectionner le Modèle:", 
            style='Custom.TLabel'
        )
        model_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        # Combobox Sélection du Modèle
        self.model_var = tk.StringVar(value='gpt-4o-mini')
        self.model_dropdown = ttk.Combobox(
            self.generate_frame,
            textvariable=self.model_var,
            state='readonly',
            values=['gpt-4o-mini', 'gpt-4o'],
            style='Custom.TCombobox'
        )
        self.model_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Label Sélection du Personnage
        character_label = ttk.Label(
            self.generate_frame, 
            text="Sélectionner le Personnage:", 
            style='Custom.TLabel'
        )
        character_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')

        # Combobox Sélection du Personnage
        self.character_dropdown = ttk.Combobox(
            self.generate_frame, 
            state='readonly',
            style='Custom.TCombobox'
        )
        self.character_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Variable d'option de génération
        self.generation_option = tk.StringVar(value='continuation')

        # Bouton "Continuer le Dialogue"
        self.continue_button = ttk.Button(
            self.generate_frame,
            text="Continuer le Dialogue",
            bootstyle="success",
            command=lambda: self.handle_generate('continuation'),
            state='disabled',
            style='Custom.TButton'
        )
        self.continue_button.grid(row=2, column=0, padx=5, pady=5, sticky='w')

        # Bouton "Obtenir des Alternatives"
        self.alternatives_button = ttk.Button(
            self.generate_frame,
            text="Obtenir des Alternatives",
            bootstyle="success",
            command=lambda: self.handle_generate('alternatives'),
            state='disabled',
            style='Custom.TButton'
        )
        self.alternatives_button.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Label du Timer
        self.timer_label = ttk.Label(
            self.generate_frame, 
            text="00:00", 
            style='Custom.TLabel'
        )
        self.timer_label.grid(row=2, column=2, padx=5, pady=5, sticky='w')

        # Frame Contexte
        self.context_frame = ttk.Frame(self.parent, padding=10, bootstyle="light")
        self.context_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        self.context_frame.grid_rowconfigure(1, weight=1)
        self.context_frame.grid_columnconfigure(0, weight=1)

        # Label Préparation
        context_label = ttk.Label(
            self.context_frame, 
            text="Préparation:", 
            style='Custom.TLabel'
        )
        context_label.grid(row=0, column=0, sticky='w', padx=5, pady=(0, 5))

        # Textbox Préparation
        self.preparation_text = tk.Text(
            self.context_frame, 
            wrap='word', 
            height=6, 
            font=("Segoe UI", 10),
            bg="#FFFFFF", 
            relief="solid",
            borderwidth=1
        )
        self.preparation_text.grid(row=1, column=0, sticky='nsew', padx=(0, 5), pady=5)

        # Scrollbar Préparation
        preparation_scroll = ttk.Scrollbar(
            self.context_frame, 
            orient='vertical', 
            command=self.preparation_text.yview, 
            bootstyle="secondary"
        )
        self.preparation_text['yscrollcommand'] = preparation_scroll.set
        preparation_scroll.grid(row=1, column=1, sticky='ns', pady=5)

        # Frame Dialogues Générés
        self.generated_dialogues_frame = ttk.Frame(self.parent, padding=10, bootstyle="light")
        self.generated_dialogues_frame.grid(row=2, column=0, sticky='nsew', pady=5)
        self.generated_dialogues_frame.grid_columnconfigure(0, weight=1)
        # Configuration des lignes internes
        self.generated_dialogues_frame.grid_rowconfigure(1, weight=1)
        self.generated_dialogues_frame.grid_rowconfigure(3, weight=1)
        self.generated_dialogues_frame.grid_rowconfigure(5, weight=1)

        self.generated_text_boxes = []

        # Premier Dialogue Généré
        label1 = ttk.Label(
            self.generated_dialogues_frame, 
            text="Dialogue Généré 1:", 
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
            borderwidth=1
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

        # Feedback Autocritic
        autocritic_label = ttk.Label(
            self.generated_dialogues_frame, 
            text="Feedback Autocritic:", 
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
            borderwidth=1
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

        # Deuxième Dialogue Généré
        label2 = ttk.Label(
            self.generated_dialogues_frame, 
            text="Dialogue Généré 2:", 
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
            borderwidth=1
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

        # Frame Contrôle
        self.control_frame = ttk.Frame(self.parent, padding=10, bootstyle="light")
        self.control_frame.grid(row=3, column=0, sticky='ew', pady=5)
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)
        self.control_frame.grid_columnconfigure(2, weight=1)

        # Variable de choix de dialogue
        self.dialogue_choice = tk.IntVar(value=1)  # Par défaut, dialogue 1

        # Bouton Sauvegarder Dialogue 1
        self.save_dialogue_1_button = ttk.Button(
            self.control_frame,
            text="Sauvegarder Dialogue 1",
            bootstyle="success",
            command=lambda: self.save_dialogue(1),
            state='disabled',
            style='Custom.TButton'
        )
        self.save_dialogue_1_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Bouton Sauvegarder Dialogue 2
        self.save_dialogue_2_button = ttk.Button(
            self.control_frame,
            text="Sauvegarder Dialogue 2",
            bootstyle="success",
            command=lambda: self.save_dialogue(2),
            state='disabled',
            style='Custom.TButton'
        )
        self.save_dialogue_2_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Bouton Reroll Dialogue
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
        """Configurer les lignes et colonnes de la grille pour un redimensionnement approprié."""
        self.parent.grid_rowconfigure(0, weight=0)  # Frame Génération
        self.parent.grid_rowconfigure(1, weight=0)  # Frame Contexte
        self.parent.grid_rowconfigure(2, weight=1)  # Frame Dialogues Générés
        self.parent.grid_rowconfigure(3, weight=0)  # Frame Contrôle
        self.parent.grid_columnconfigure(0, weight=1)

    # Méthodes spécifiques au cadre droit
    def handle_generate(self, option):
        """Gérer les actions lors de la génération de dialogues."""
        self.generation_option.set(option)
        self.start_timer()
        self.generate_dialogue()

    def enable_generate_buttons(self):
        """Activer les boutons de génération."""
        self.continue_button.config(state='normal')
        self.alternatives_button.config(state='normal')

    def update_character_dropdown(self, characters):
        """Mettre à jour le dropdown des personnages avec une liste de noms."""
        self.character_dropdown['values'] = characters
        if characters:
            self.character_dropdown.current(0)

    def get_selected_character(self):
        """Retourner le personnage sélectionné depuis le dropdown."""
        return self.character_dropdown.get()

    def get_selected_model(self):
        """Retourner le modèle sélectionné depuis le dropdown."""
        return self.model_var.get()

    def get_generation_option(self):
        """Obtenir l'option de génération sélectionnée."""
        return self.generation_option.get()

    def get_preparation_text(self):
        """Récupérer le texte depuis le widget de préparation."""
        return self.preparation_text.get("1.0", "end-1c")

    def generate_dialogue(self):
        """Générer la prochaine ligne de dialogue via le contrôleur et arrêter le timer."""
        logging.info("Génération de la prochaine ligne de dialogue dans RightFrame")
        self.main_gui.controller.generate_dialogue()

    def on_dialogue_generated(self):
        """Méthode de callback appelée après la génération du dialogue."""
        self.stop_timer()

    def display_preparation_text(self, text):
        """Afficher le texte de préparation dans la textbox."""
        self.preparation_text.delete(1.0, tk.END)
        self.preparation_text.insert(tk.END, text)

    def display_generated_dialogue(self, dialogue_1, dialogue_2):
        """Afficher les dialogues générés."""
        self.generated_text_boxes[0].delete(1.0, tk.END)
        self.generated_text_boxes[0].insert(tk.END, dialogue_1)
        self.generated_text_boxes[1].delete(1.0, tk.END)
        self.generated_text_boxes[1].insert(tk.END, dialogue_2)
        self.save_dialogue_1_button.config(state='normal')
        self.save_dialogue_2_button.config(state='normal')
        self.reroll_button.config(state='normal')

        # Si l'option est 'alternatives', désactiver la textbox de préparation
        if self.get_generation_option() == 'alternatives':
            self.preparation_text.config(state='disabled')
        else:
            self.preparation_text.config(state='normal')

    def save_dialogue(self, dialogue_number):
        """Sauvegarder le dialogue sélectionné."""
        # Implémenter la logique de sauvegarde ici
        logging.info(f"Sauvegarde du Dialogue {dialogue_number}")
        # Exemple: self.main_gui.controller.save_dialogue(dialogue_number)

    def reroll_dialogue(self):
        """Reroll pour générer un nouveau dialogue."""
        logging.info("Rerolling dialogue")
        self.generate_dialogue()
