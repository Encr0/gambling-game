import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
import time

INITIAL_MONEY = 1000
SYMBOLS = ["🍒", "💎", "🔔", "🍋", "7️⃣"]
THEME_COLORS = {
    "light": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "button": "#e0e0e0",
        "highlight": "#4a7abc",
        "accent": "#ff9800"
    },
    "dark": {
        "bg": "#2d2d2d",
        "fg": "#ffffff",
        "button": "#3d3d3d",
        "highlight": "#5294e2",
        "accent": "#ff9800"
    }
}

class SlotMachine:
    def __init__(self, parent, casino_app):
        self.parent = parent
        self.casino_app = casino_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("🎰 Tragamonedas")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        self.window.config(bg=THEME_COLORS[casino_app.theme]["bg"])
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        self.spinning = False
        self.symbols = []
        self.after_ids = []
    
    def create_widgets(self):
        self.title_label = tk.Label(
            self.window,
            text="🎰 Tragamonedas 🎰",
            font=("Arial", 24, "bold"),
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"]
        )
        self.title_label.pack(pady=20)
        
        self.balance_label = tk.Label(
            self.window,
            text=f"💰 Saldo: ${self.casino_app.balance}",
            font=("Arial", 14),
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"]
        )
        self.balance_label.pack(pady=10)
        
        self.symbols_frame = tk.Frame(
            self.window,
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            highlightbackground=THEME_COLORS[self.casino_app.theme]["highlight"],
            highlightthickness=2,
            padx=20,
            pady=20
        )
        self.symbols_frame.pack(pady=20)
        
        self.symbol_labels = []
        for i in range(3):
            label = tk.Label(
                self.symbols_frame,
                text="❓",
                font=("Arial", 36),
                width=3,
                height=2,
                relief="ridge",
                bg=THEME_COLORS[self.casino_app.theme]["button"],
                fg=THEME_COLORS[self.casino_app.theme]["fg"]
            )
            label.grid(row=0, column=i, padx=10)
            self.symbol_labels.append(label)
        
        self.bet_frame = tk.Frame(
            self.window,
            bg=THEME_COLORS[self.casino_app.theme]["bg"]
        )
        self.bet_frame.pack(pady=10)
        
        self.bet_label = tk.Label(
            self.bet_frame,
            text="Apuesta ($): ",
            font=("Arial", 14),
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"]
        )
        self.bet_label.grid(row=0, column=0, padx=5)

        self.bet_var = tk.StringVar()
        self.bet_var.set("10")  # apuesta default = 10
        
        vcmd = (self.window.register(self.validate_bet), '%P')
        
        self.bet_entry = tk.Entry(
            self.bet_frame,
            textvariable=self.bet_var,
            font=("Arial", 14),
            width=10,
            validate="key",
            validatecommand=vcmd
        )
        self.bet_entry.grid(row=0, column=1, padx=5)

        self.spin_button = tk.Button(
            self.window,
            text="🎮 Girar",
            font=("Arial", 16, "bold"),
            bg=THEME_COLORS[self.casino_app.theme]["accent"],
            fg="#ffffff",
            width=15,
            height=2,
            command=self.spin
        )
        self.spin_button.pack(pady=20)
        

        self.result_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 16, "bold"),
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            fg=THEME_COLORS[self.casino_app.theme]["accent"]
        )
        self.result_label.pack(pady=10)

        self.close_button = tk.Button(
            self.window,
            text="🚪 Cerrar",
            font=("Arial", 12),
            bg=THEME_COLORS[self.casino_app.theme]["button"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"],
            command=self.window.destroy
        )
        self.close_button.pack(pady=10)
    
    def validate_bet(self, new_value):
        if new_value == "":
            return True
        
        if not new_value.isdigit():
            return False
        
        if int(new_value) <= 0:
            return False
        
        if int(new_value) > self.casino_app.balance:
            return False
            
        return True
    
    def spin(self):
        if self.spinning:
            return
        
        try:
            bet = int(self.bet_var.get())
            if bet <= 0:
                messagebox.showerror("Error", "La apuesta debe ser mayor a cero.")
                return
            
            if bet > self.casino_app.balance:
                messagebox.showerror("Error", "No tienes suficiente saldo para esta apuesta.")
                return
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un número válido.")
            return
        
        self.spinning = True
        self.result_label.config(text="")
        self.spin_button.config(state=tk.DISABLED)
        self.animate_spin(bet)
    
    def animate_spin(self, bet):
        for after_id in self.after_ids:
            self.window.after_cancel(after_id)
        self.after_ids = []
        
        self.symbols = []
        spin_duration = 2000
        animation_steps = 20
        interval = spin_duration / animation_steps
        
        def update_symbols(step):
            if step < animation_steps:
                for i, label in enumerate(self.symbol_labels):
                    random_symbol = random.choice(SYMBOLS)
                    label.config(text=random_symbol)
                
                after_id = self.window.after(int(interval), lambda: update_symbols(step + 1))
                self.after_ids.append(after_id)
            else:
                self.symbols = [random.choice(SYMBOLS) for _ in range(3)]
                
                for i, label in enumerate(self.symbol_labels):
                    label.config(text=self.symbols[i])
                
                self.check_result(bet)
        
        update_symbols(0)
    
    def check_result(self, bet):
        unique_symbols = set(self.symbols)
        
        if len(unique_symbols) == 1:
            winnings = bet * 5
            result_text = f"¡GANASTE! 🎉 Todos los símbolos coinciden.\nGanancia: ${winnings}"
            self.casino_app.update_balance(winnings, is_win=True)
        elif len(unique_symbols) == 2:
            winnings = bet * 2
            result_text = f"¡GANASTE! 🎉 Dos símbolos coinciden.\nGanancia: ${winnings}"
            self.casino_app.update_balance(winnings, is_win=True)
        else:
            result_text = f"😢 No hay coincidencias.\nPérdida: ${bet}"
            self.casino_app.update_balance(-bet, is_win=False)
        
        self.result_label.config(text=result_text)
        self.balance_label.config(text=f"💰 Saldo: ${self.casino_app.balance}")
        self.spin_button.config(state=tk.NORMAL)
        self.spinning = False

class ScratchCard:
    def __init__(self, parent, casino_app):
        self.parent = parent
        self.casino_app = casino_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("🎟️ Rasca y Gana")
        self.window.geometry("800x800")
        self.window.resizable(False, False)
        self.window.config(bg=THEME_COLORS[casino_app.theme]["bg"])
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self.scratched = False
        self.symbols = []
        self.card_buttons = []
        self.bet_amount = 20  # cuanto cuestan los rasca y gana
        
        self.create_widgets()
    
    def create_widgets(self):
        self.title_label = tk.Label(
            self.window,
            text="🎟️ Rasca y Gana 🎟️",
            font=("Arial", 24, "bold"),
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"]
        )
        self.title_label.pack(pady=20)
        
        self.balance_label = tk.Label(
            self.window,
            text=f"💰 Saldo: ${self.casino_app.balance}",
            font=("Arial", 14),
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"]
        )
        self.balance_label.pack(pady=10)
        
        self.instructions_label = tk.Label(
            self.window,
            text=f"Costo por tarjeta: ${self.bet_amount}\nHaz clic en 'Rascar' para revelar los símbolos.\nNecesitas 3 o más símbolos iguales para ganar.",
            font=("Arial", 12),
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"],
            justify=tk.CENTER
        )
        self.instructions_label.pack(pady=10)

        self.grid_frame = tk.Frame(
            self.window,
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            highlightbackground=THEME_COLORS[self.casino_app.theme]["highlight"],
            highlightthickness=3,
            padx=20,
            pady=20
        )
        self.grid_frame.pack(pady=20)
        
        self.card_buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                button = tk.Button(
                    self.grid_frame,
                    text="❓",
                    font=("Arial", 24),
                    width=3,
                    height=2,
                    bg=THEME_COLORS[self.casino_app.theme]["accent"],
                    fg="#ffffff",
                    state=tk.DISABLED
                )
                button.grid(row=i, column=j, padx=5, pady=5)
                row.append(button)
            self.card_buttons.append(row)
        
        self.scratch_button = tk.Button(
            self.window,
            text="🪙 Rascar",
            font=("Arial", 16, "bold"),
            bg=THEME_COLORS[self.casino_app.theme]["highlight"],
            fg="#ffffff",
            width=15,
            height=2,
            command=self.scratch_card
        )
        self.scratch_button.pack(pady=20)
        
        self.result_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 16, "bold"),
            bg=THEME_COLORS[self.casino_app.theme]["bg"],
            fg=THEME_COLORS[self.casino_app.theme]["accent"]
        )
        self.result_label.pack(pady=10)
        
        self.buttons_frame = tk.Frame(
            self.window,
            bg=THEME_COLORS[self.casino_app.theme]["bg"]
        )
        self.buttons_frame.pack(pady=10)

        self.new_card_button = tk.Button(
            self.buttons_frame,
            text="🎟️ Nueva Tarjeta",
            font=("Arial", 12),
            bg=THEME_COLORS[self.casino_app.theme]["button"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"],
            command=self.new_card,
            state=tk.DISABLED
        )
        self.new_card_button.grid(row=0, column=0, padx=5)

        self.close_button = tk.Button(
            self.buttons_frame,
            text="🚪 Cerrar",
            font=("Arial", 12),
            bg=THEME_COLORS[self.casino_app.theme]["button"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"],
            command=self.window.destroy
        )
        self.close_button.grid(row=0, column=1, padx=5)
    
    def scratch_card(self):
        if self.scratched:
            return
        
        if self.casino_app.balance < self.bet_amount:
            messagebox.showerror("Error", "No tienes suficiente saldo para comprar una tarjeta.")
            return
        
        self.symbols = []
        for i in range(3):
            row = []
            for j in range(3):
                symbol = random.choice(SYMBOLS)
                row.append(symbol)
            self.symbols.append(row)
        
        self.animate_scratch()
        self.scratched = True
        self.scratch_button.config(state=tk.DISABLED)
        self.new_card_button.config(state=tk.NORMAL)
    
    def animate_scratch(self):
        positions = []
        for i in range(3):
            for j in range(3):
                positions.append((i, j))
        
        random.shuffle(positions)
        delay = 300
        
        for idx, (i, j) in enumerate(positions):
            self.window.after(
                idx * delay,
                lambda row=i, col=j: self.reveal_symbol(row, col)
            )
        
        self.window.after(
            len(positions) * delay + 100,
            self.check_result
        )
    
    def reveal_symbol(self, row, col):
        symbol = self.symbols[row][col]
        self.card_buttons[row][col].config(
            text=symbol,
            bg=THEME_COLORS[self.casino_app.theme]["button"],
            fg=THEME_COLORS[self.casino_app.theme]["fg"]
        )
    
    def check_result(self):
        self.casino_app.update_balance(-self.bet_amount, is_win=False)
        
        symbol_count = {}
        for row in self.symbols:
            for symbol in row:
                symbol_count[symbol] = symbol_count.get(symbol, 0) + 1
        
        max_count = max(symbol_count.values())
        
        if max_count >= 3:
            if max_count == 9:
                winnings = self.bet_amount * 100
                result_text = f"🎰 ¡JACKPOT! 🎰\nTodos los símbolos coinciden.\nGanancia: ${winnings}"
            elif max_count >= 5:
                winnings = self.bet_amount * 10
                result_text = f"🤑 ¡Excelente! {max_count} símbolos coinciden.\nGanancia: ${winnings}"
            elif max_count == 4:
                winnings = self.bet_amount * 5
                result_text = f"😊 ¡Bien! {max_count} símbolos coinciden.\nGanancia: ${winnings}"
            else:
                winnings = self.bet_amount * 2
                result_text = f"🙂 ¡Ganaste! {max_count} símbolos coinciden.\nGanancia: ${winnings}"
            
            self.casino_app.update_balance(winnings, is_win=True)
            
        else:
            result_text = f"😢 No hay suficientes símbolos iguales.\nPérdida: ${self.bet_amount}"
        
        self.result_label.config(text=result_text)
        self.balance_label.config(text=f"💰 Saldo: ${self.casino_app.balance}")
    
    def new_card(self):
        self.scratched = False
        
        for i in range(3):
            for j in range(3):
                self.card_buttons[i][j].config(
                    text="❓",
                    bg=THEME_COLORS[self.casino_app.theme]["accent"],
                    fg="#ffffff",
                    state=tk.DISABLED
                )
        
        self.scratch_button.config(state=tk.NORMAL)
        self.new_card_button.config(state=tk.DISABLED)
        self.result_label.config(text="")

class CasinoGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎰 Casino Virtual")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        self.balance = INITIAL_MONEY
        self.theme = "light"
        self.apply_theme()
        
        self.main_frame = tk.Frame(self.root, bg=THEME_COLORS[self.theme]["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.title_label = tk.Label(
            self.main_frame, 
            text="🎰 Casino Virtual", 
            font=("Arial", 24, "bold"),
            bg=THEME_COLORS[self.theme]["bg"],
            fg=THEME_COLORS[self.theme]["fg"]
        )
        self.title_label.pack(pady=20)
        
        # Create label for balance
        self.balance_frame = tk.Frame(self.main_frame, bg=THEME_COLORS[self.theme]["bg"])
        self.balance_frame.pack(pady=10)
        
        self.balance_label = tk.Label(
            self.balance_frame,
            text=f"💰 Saldo: ${self.balance}",
            font=("Arial", 16),
            bg=THEME_COLORS[self.theme]["bg"],
            fg=THEME_COLORS[self.theme]["fg"]
        )
        self.balance_label.pack()
        
        self.stats_frame = tk.Frame(self.main_frame, bg=THEME_COLORS[self.theme]["bg"])
        self.stats_frame.pack(pady=5)
        
        self.won_label = tk.Label(
            self.stats_frame,
            text="🤑 Ganado: $0",
            font=("Arial", 12),
            bg=THEME_COLORS[self.theme]["bg"],
            fg=THEME_COLORS[self.theme]["fg"]
        )
        self.won_label.pack(side=tk.LEFT, padx=10)
        
        self.lost_label = tk.Label(
            self.stats_frame,
            text="😭 Perdido: $0",
            font=("Arial", 12),
            bg=THEME_COLORS[self.theme]["bg"],
            fg=THEME_COLORS[self.theme]["fg"]
        )
        self.lost_label.pack(side=tk.LEFT, padx=10)

        self.button_frame = tk.Frame(self.main_frame, bg=THEME_COLORS[self.theme]["bg"])
        self.button_frame.pack(pady=20)
        

        self.slot_button = tk.Button(
            self.button_frame,
            text="🎰 Jugar Tragamonedas",
            font=("Arial", 14),
            bg=THEME_COLORS[self.theme]["button"],
            fg=THEME_COLORS[self.theme]["fg"],
            width=20,
            height=2,
            command=self.open_slot_machine
        )
        self.slot_button.grid(row=0, column=0, padx=10, pady=10)
        
        self.scratch_button = tk.Button(
            self.button_frame,
            text="🎟️ Jugar Rasca y Gana",
            font=("Arial", 14),
            bg=THEME_COLORS[self.theme]["button"],
            fg=THEME_COLORS[self.theme]["fg"],
            width=20,
            height=2,
            command=self.open_scratch_card
        )
        self.scratch_button.grid(row=0, column=1, padx=10, pady=10)
        
        self.balance_button = tk.Button(
            self.button_frame,
            text="💰 Ver Saldo Actual",
            font=("Arial", 14),
            bg=THEME_COLORS[self.theme]["button"],
            fg=THEME_COLORS[self.theme]["fg"],
            width=20,
            height=2,
            command=self.show_balance
        )
        self.balance_button.grid(row=1, column=0, padx=10, pady=10)
        
        self.exit_button = tk.Button(
            self.button_frame,
            text="🚪 Salir del Juego",
            font=("Arial", 14),
            bg=THEME_COLORS[self.theme]["button"],
            fg=THEME_COLORS[self.theme]["fg"],
            width=20,
            height=2,
            command=self.exit_game
        )
        self.exit_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Theme toggle button
        self.theme_button = tk.Button(
            self.main_frame,
            text="🌙 Cambiar a Tema Oscuro" if self.theme == "light" else "☀️ Cambiar a Tema Claro",
            font=("Arial", 12),
            bg=THEME_COLORS[self.theme]["button"],
            fg=THEME_COLORS[self.theme]["fg"],
            command=self.toggle_theme
        )
        self.theme_button.pack(pady=10)
        

        self.total_won = 0
        self.total_lost = 0
        
        self.load_game_data()
    
    def apply_theme(self):
        self.root.config(bg=THEME_COLORS[self.theme]["bg"])
    
    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()
        self.theme_button.config(
            text="🌙 Cambiar a Tema Oscuro" if self.theme == "light" else "☀️ Cambiar a Tema Claro",
            bg=THEME_COLORS[self.theme]["button"],
            fg=THEME_COLORS[self.theme]["fg"]
        )
        
        self.main_frame.config(bg=THEME_COLORS[self.theme]["bg"])
        self.title_label.config(bg=THEME_COLORS[self.theme]["bg"], fg=THEME_COLORS[self.theme]["fg"])
        self.balance_frame.config(bg=THEME_COLORS[self.theme]["bg"])
        self.balance_label.config(bg=THEME_COLORS[self.theme]["bg"], fg=THEME_COLORS[self.theme]["fg"])
        self.stats_frame.config(bg=THEME_COLORS[self.theme]["bg"])
        self.won_label.config(bg=THEME_COLORS[self.theme]["bg"], fg=THEME_COLORS[self.theme]["fg"])
        self.lost_label.config(bg=THEME_COLORS[self.theme]["bg"], fg=THEME_COLORS[self.theme]["fg"])
        self.button_frame.config(bg=THEME_COLORS[self.theme]["bg"])
        
        for button in [self.slot_button, self.scratch_button, self.balance_button, self.exit_button]:
            button.config(bg=THEME_COLORS[self.theme]["button"], fg=THEME_COLORS[self.theme]["fg"])
    
    def open_slot_machine(self):
        SlotMachine(self.root, self)
        
    def open_scratch_card(self):
        ScratchCard(self.root, self)
    
    def show_balance(self):
        messagebox.showinfo("💰 Saldo Actual", f"Tu saldo actual es: ${self.balance}\n\nHas ganado: ${self.total_won}\nHas perdido: ${self.total_lost}")
    
    def exit_game(self):
        self.save_game_data()
        self.root.destroy()
    
    def update_balance(self, amount, is_win=True):
        self.balance += amount
        if is_win and amount > 0:
            self.total_won += amount
        elif not is_win and amount < 0:
            self.total_lost += abs(amount)
        
        self.balance_label.config(text=f"💰 Saldo: ${self.balance}")
        self.won_label.config(text=f"🤑 Ganado: ${self.total_won}")
        self.lost_label.config(text=f"😭 Perdido: ${self.total_lost}")
    
    def save_game_data(self):
        data = {
            "balance": self.balance,
            "total_won": self.total_won,
            "total_lost": self.total_lost,
            "theme": self.theme
        }
        
        try:
            with open("casino_data.json", "w") as file:
                json.dump(data, file)
        except Exception as e:
            print(f"Error saving game data: {e}")
    
    def load_game_data(self):
        try:
            if os.path.exists("casino_data.json"):
                with open("casino_data.json", "r") as file:
                    data = json.load(file)
                    self.balance = data.get("balance", INITIAL_MONEY)
                    self.total_won = data.get("total_won", 0)
                    self.total_lost = data.get("total_lost", 0)
                    self.theme = data.get("theme", "light")
                    
                    self.balance_label.config(text=f"💰 Saldo: ${self.balance}")
                    self.won_label.config(text=f"🤑 Ganado: ${self.total_won}")
                    self.lost_label.config(text=f"😭 Perdido: ${self.total_lost}")
                    self.apply_theme()
        except Exception as e:
            print(f"Error loading game data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CasinoGame(root)
    root.mainloop()
