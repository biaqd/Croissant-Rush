
'''
import tkinter as tk
root=tk.Tk()
root.title("Croissant Rush")
root.geometry("500x500")
root.mainloop()
'''

import tkinter as tk
from tkinter import messagebox
import random
import json
import os

class CroissantRush:
    def __init__(self, root):
        self.root = root
        self.root.title("Croissant Rush")
        self.root.geometry("500x600")
        
        # File System Setup
        self.score_file = "scores.json"
        self.high_scores = self.load_scores()
        
        self.running = False
        self.items = []
        self.score = 0
        
        # Difficulty Settings: {Speed, Spawn Rate}
        self.levels = {
            "Breeze": (3, 1500),
            "Easy":   (5, 1200),
            "Medium": (8, 800),
            "Hard":   (12, 500)
        }
        
        self.show_menu()

    # --- DATA MANIPULATION (File System) ---
    def load_scores(self):
        if os.path.exists(self.score_file):
            try:
                with open(self.score_file, "r") as f:
                    return json.load(f)
            except: return []
        return []

    def save_new_score(self):
        """INSERT and UPDATE logic"""
        self.high_scores.append(self.score)
        # Keep top 5 only
        self.high_scores = sorted(self.high_scores, reverse=True)[:5]
        with open(self.score_file, "w") as f:
            json.dump(self.high_scores, f)

    # --- GUI SCREENS ---
    def show_menu(self):
        self.menu_frame = tk.Frame(self.root, bg="#F5DEB3")
        self.menu_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        tk.Label(self.menu_frame, text="🥐 Croissant Rush 🥐", font=("Arial", 24, "bold"), bg="#F5DEB3").pack(pady=20)
        
        tk.Label(self.menu_frame, text="Select Difficulty:", bg="#F5DEB3").pack()
        self.diff_var = tk.StringVar(value="Easy")
        for lvl in self.levels.keys():
            tk.Radiobutton(self.menu_frame, text=lvl, variable=self.diff_var, value=lvl, bg="#F5DEB3").pack()

        tk.Button(self.menu_frame, text="PLAY", command=self.start_game, width=15, bg="#8B4513", fg="white").pack(pady=10)
        tk.Button(self.menu_frame, text="SCOREBOARD", command=self.show_scores, width=15).pack()

    def show_scores(self):
        scores = "\n".join([f"Rank {i+1}: {s}" for i, s in enumerate(self.high_scores)])
        messagebox.showinfo("Scoreboard", scores if scores else "No records yet!")

    # --- GAME LOGIC ---
    def start_game(self):
        self.menu_frame.place_forget()
        self.running = True
        self.score = 0
        self.items = []
        
        self.canvas = tk.Canvas(self.root, width=500, height=600, bg="#FFF8DC")
        self.canvas.pack()
        
        self.score_txt = self.canvas.create_text(60, 20, text=f"Score: {self.score}", font=("Arial", 14))
        
        diff_name = self.diff_var.get()
        self.speed, self.spawn_rate = self.levels[diff_name]
        
        self.spawn_loop()
        self.game_loop()

    def spawn_loop(self):
        if not self.running: return
        
        x = random.randint(30, 470)
        is_pizza = random.random() < 0.2
        color = "#FF6347" if is_pizza else "#FFD700" # Pizza vs Good
        
        # Draw Croissant
        item_id = self.canvas.create_oval(x, -50, x+40, -10, fill=color, outline="brown")
        
        # Click Event: Tag Bind
        self.canvas.tag_bind(item_id, "<Button-1>", lambda e, i=item_id, p=is_pizza: self.handle_click(i, p))
        
        self.items.append({"id": item_id, "is_pizza": is_pizza})
        self.root.after(self.spawn_rate, self.spawn_loop)

    def handle_click(self, item_id, is_pizza):
        if is_pizza:
            self.end_game("Tragedy! You touched a Pizza Croissant!")
        else:
            self.score += 10
            self.canvas.itemconfig(self.score_txt, text=f"Score: {self.score}")
            self.canvas.delete(item_id)
            self.items = [i for i in self.items if i["id"] != item_id]

    def game_loop(self):
        if not self.running: return
        
        for item_data in self.items[:]:
            item = item_data["id"]
            self.canvas.move(item, 0, self.speed)
            
            y2 = self.canvas.coords(item)[3]
            if y2 > 600: # Reached bottom
                if not item_data["is_pizza"]:
                    # Missed a good croissant penalty
                    self.score = max(0, self.score - 5)
                    self.canvas.itemconfig(self.score_txt, text=f"Score: {self.score}")
                
                self.canvas.delete(item)
                self.items.remove(item_data)

        self.root.after(30, self.game_loop)

    def end_game(self, msg):
        self.running = False
        self.save_new_score()
        messagebox.showinfo("Game Over", f"{msg}\nFinal Score: {self.score}")
        self.canvas.destroy()
        self.show_menu()

if __name__ == "__main__":
    root = tk.Tk()
    game = CroissantRush(root)
    root.mainloop()