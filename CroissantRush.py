import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from PIL import Image, ImageTk

class CroissantRush:
    def __init__(self, root):
        self.root = root
        self.root.title("Croissant Rush")
        self.root.geometry("500x700")
        
        # 1. LOAD & RESIZE ASSETS
        # We resize them here so they don't clutter the screen
        self.bg_img = ImageTk.PhotoImage(Image.open("pixelcafe.png").resize((500, 700)))
        self.good_img = ImageTk.PhotoImage(Image.open("croissant.png").resize((60, 60)))
        self.bad_img = ImageTk.PhotoImage(Image.open("pizzacroissant.png").resize((60, 60)))
        
        self.running = False
        self.score = 0
        self.speed_multiplier = 1.0
        self.items = []
        
        self.show_menu()

    def show_menu(self):
        self.menu_frame = tk.Frame(self.root, bg="#F5DEB3")
        self.menu_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        tk.Label(self.menu_frame, text="CROISSANT RUSH", font=("Courier", 30, "bold"), bg="#F5DEB3").pack(pady=50)
        tk.Button(self.menu_frame, text="PLAY", font=("Arial", 18), command=self.start_game, width=10).pack(pady=20)

    def start_game(self):
        if hasattr(self, 'menu_frame'):
            self.menu_frame.place_forget()
        
        self.score = 0
        self.speed_multiplier = 1.0
        self.running = True
        self.items = []
        
        # CREATE CANVAS
        self.canvas = tk.Canvas(self.root, width=500, height=700)
        self.canvas.pack()
        
        # DRAW BACKGROUND
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        
        self.score_display = self.canvas.create_text(80, 30, text=f"Score: {self.score}", 
                                                     font=("Arial", 16, "bold"), fill="white")
        
        self.spawn_loop()
        self.game_loop()

    def spawn_loop(self):
        if not self.running: return
        
        x = random.randint(50, 450)
        is_good = random.random() > 0.25
        img = self.good_img if is_good else self.bad_img
        
        # Using anchor="center" makes the movement math much easier
        item_id = self.canvas.create_image(x, -50, image=img, anchor="center")
        
        self.canvas.tag_bind(item_id, "<Button-1>", lambda e, i=item_id, g=is_good: self.process_click(i, g))
        self.items.append({"id": item_id, "is_good": is_good})
        
        interval = max(400, int(1200 / self.speed_multiplier))
        self.root.after(interval, self.spawn_loop)

    def process_click(self, item_id, is_good):
        if not self.running: return
        if is_good:
            self.score += 10
            self.canvas.itemconfig(self.score_display, text=f"Score: {self.score}")
            if self.score % 50 == 0:
                self.speed_multiplier += 0.1
            self.canvas.delete(item_id)
            self.items = [i for i in self.items if i["id"] != item_id]
        else:
            self.end_game_flow()

    def game_loop(self):
        if not self.running: return
        
        current_speed = 5 * self.speed_multiplier
        
        for item_data in self.items[:]:
            item = item_data["id"]
            self.canvas.move(item, 0, current_speed)
            
            # THE FIX: Image coords only have [x, y]. coords[1] is the vertical position.
            coords = self.canvas.coords(item)
            if coords and coords[1] > 750: 
                if item_data["is_good"]:
                    self.score = max(0, self.score - 5)
                    self.canvas.itemconfig(self.score_display, text=f"Score: {self.score}")
                
                self.canvas.delete(item)
                if item_data in self.items:
                    self.items.remove(item_data)

        self.root.after(30, self.game_loop)

    def end_game_flow(self):
        self.running = False
        play_again = messagebox.askyesno("GAME OVER", f"Final Score: {self.score}\nPlay again?")
        self.canvas.destroy()
        if play_again:
            self.start_game()
        else:
            self.show_menu()

if __name__ == "__main__":
    root = tk.Tk()
    game = CroissantRush(root)
    root.mainloop()