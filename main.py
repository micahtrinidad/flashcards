import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style
import db

class FlashcardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flashcards")
        self.geometry("520x320")
        self.resizable(False, False)

        db.init_db()

        # State
        self.decks = []              # list of (id, name)
        self.selected_deck_id = None
        self.current_card = None     # (id, term, definition)
        self.answer_shown = False

        # UI
        self._build_ui()
        self._refresh_decks()

    def _build_ui(self):
        # Top bar: deck selection + buttons
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")

        ttk.Label(top, text="Deck:").pack(side="left")

        self.deck_var = tk.StringVar()
        self.deck_combo = ttk.Combobox(top, textvariable=self.deck_var, state="readonly", width=25)
        self.deck_combo.pack(side="left", padx=8)
        self.deck_combo.bind("<<ComboboxSelected>>", self.on_deck_selected)

        ttk.Button(top, text="New Deck", command=self.new_deck_dialog).pack(side="left", padx=6)
        ttk.Button(top, text="Add Card", command=self.add_card_dialog).pack(side="left")

        # Card area
        card_frame = ttk.Frame(self, padding=12)
        card_frame.pack(fill="both", expand=True)

        self.term_label = ttk.Label(card_frame, text="Select a deck to start", font=("Segoe UI", 16))
        self.term_label.pack(pady=(30, 10))

        self.answer_label = ttk.Label(card_frame, text="", font=("Segoe UI", 14))
        self.answer_label.pack(pady=(0, 10))

        self.count_label = ttk.Label(card_frame, text="")
        self.count_label.pack()

        # Bottom buttons
        bottom = ttk.Frame(self, padding=12)
        bottom.pack(fill="x")

        self.show_btn = ttk.Button(bottom, text="Show Answer", command=self.show_answer, state="disabled")
        self.show_btn.pack(side="left")

        self.next_btn = ttk.Button(bottom, text="Next", command=self.next_card, state="disabled")
        self.next_btn.pack(side="left", padx=8)

        ttk.Button(bottom, text="Quit", command=self.destroy).pack(side="right")

    # -------------------- Deck management --------------------

    def _refresh_decks(self):
        self.decks = db.get_decks()
        deck_names = [name for _, name in self.decks]
        self.deck_combo["values"] = deck_names

        if not deck_names:
            self.deck_var.set("")
            self.selected_deck_id = None
            self._set_no_card_state("Create a deck to start")
            return

        # Auto-select first deck if none selected
        current = self.deck_var.get()
        if current not in deck_names:
            self.deck_var.set(deck_names[0])
        self.on_deck_selected()

    def on_deck_selected(self, event=None):
        name = self.deck_var.get()
        deck_id = None
        for did, dname in self.decks:
            if dname == name:
                deck_id = did
                break

        self.selected_deck_id = deck_id
        self.next_card()

    def new_deck_dialog(self):
        win = tk.Toplevel(self)
        win.title("New Deck")
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="Deck name:").pack(padx=12, pady=(12, 4))
        entry = ttk.Entry(win, width=30)
        entry.pack(padx=12, pady=4)
        entry.focus()

        def create():
            name = entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Deck name cannot be empty.", parent=win)
                return
            try:
                db.create_deck(name)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)
                return
            win.destroy()
            self._refresh_decks()
            self.deck_var.set(name)
            self.on_deck_selected()

        ttk.Button(win, text="Create", command=create).pack(padx=12, pady=(8, 12))

    # -------------------- Cards --------------------

    def add_card_dialog(self):
        if self.selected_deck_id is None:
            messagebox.showinfo("No deck", "Create/select a deck first.")
            return

        win = tk.Toplevel(self)
        win.title("Add Card")
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="Spanish term:").pack(padx=12, pady=(12, 4))
        term_entry = ttk.Entry(win, width=40)
        term_entry.pack(padx=12, pady=4)
        term_entry.focus()

        ttk.Label(win, text="English definition:").pack(padx=12, pady=(10, 4))
        def_entry = ttk.Entry(win, width=40)
        def_entry.pack(padx=12, pady=4)

        def save():
            term = term_entry.get().strip()
            definition = def_entry.get().strip()
            if not term or not definition:
                messagebox.showerror("Error", "Both fields are required.", parent=win)
                return

            try:
                db.add_card(self.selected_deck_id, term, definition)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)
                return

            win.destroy()
            # Show a fresh card after adding
            self.next_card()

        ttk.Button(win, text="Save", command=save).pack(padx=12, pady=(10, 12))

    def next_card(self):
        if self.selected_deck_id is None:
            self._set_no_card_state("Select a deck to start")
            return

        total = db.count_cards(self.selected_deck_id)
        if total == 0:
            self._set_no_card_state("No cards yet. Click “Add Card”.")
            return

        self.current_card = db.get_random_card(self.selected_deck_id)
        self.answer_shown = False

        _, term, definition = self.current_card
        self.term_label.config(text=term)
        self.answer_label.config(text="")  # hidden
        self.count_label.config(text=f"{total} card(s) in this deck")

        self.show_btn.config(state="normal")
        self.next_btn.config(state="normal")

    def show_answer(self):
        if not self.current_card:
            return
        _, _, definition = self.current_card
        self.answer_label.config(text=definition)
        self.answer_shown = True

    def _set_no_card_state(self, msg: str):
        self.current_card = None
        self.term_label.config(text=msg)
        self.answer_label.config(text="")
        self.count_label.config(text="")
        self.show_btn.config(state="disabled")
        self.next_btn.config(state="disabled")


if __name__ == "__main__":
    app = FlashcardApp()
    app.mainloop()

