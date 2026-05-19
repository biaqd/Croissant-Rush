import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk

# Variables globales
score = 0
lives = 0
speed_multiplier = 1.0
running = False
items = []

def show_menu():
    global menu_frame
    menu_frame = tk.Frame(root, bg="#F5DEB3")
    menu_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(menu_frame, text="CROISSANT RUSH", font=("Courier", 30, "bold"), bg="#F5DEB3").pack(pady=50)
    tk.Button(menu_frame, text="PLAY", font=("Arial", 18), command=difficulty_selection, width=30).pack(pady=20)
    tk.Button(menu_frame, text="CREDITS", font=("Arial", 18), command=credits, width=30).pack(pady=20)
    tk.Button(menu_frame, text="QUIT", font=("Arial", 18), command=root.quit, width=30).pack(pady=20)

def credits():
    credits_frame = tk.Frame(root, bg="#F5DEB3")
    credits_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(credits_frame, text="CREDITS", font=("Courier", 24, "bold"), bg="#F5DEB3").pack(pady=20)
    tk.Label(credits_frame, text="Thank you for playing!\n \nThis game is inspired by an arcade games\n \nDeveloped by Paris Baguette Team", font=("Arial", 18), bg="#F5DEB3").pack(pady=40)
    tk.Button(credits_frame, text="BACK TO MENU", font=("Arial", 18), command=lambda: [credits_frame.destroy(), show_menu()],width=30).pack(pady=60)


def difficulty_selection():
    difficulty_frame = tk.Frame(root, bg="#F5DEB3")
    difficulty_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(difficulty_frame, text="SELECT DIFFICULTY", font=("Courier", 24, "bold"), bg="#F5DEB3").pack(pady=50)
    tk.Button(difficulty_frame, text="EASY (5 life)", font=("Arial", 18), command=lambda: [difficulty_frame.destroy(), start_game("easy")], width=30).pack(pady=20)
    tk.Button(difficulty_frame, text="MEDIUM (3 life)", font=("Arial", 18), command=lambda: [difficulty_frame.destroy(), start_game("medium")], width=30).pack(pady=20)
    tk.Button(difficulty_frame, text="HARD (1 life)", font=("Arial", 18), command=lambda: [difficulty_frame.destroy(), start_game("hard")], width=30).pack(pady=20)


    
def start_game(level):
    global score, speed_multiplier, running, items, canvas, score_display, lives_display, lives
    
    if level == "easy":
        lives = 5
    elif level == "medium":
        lives = 3
    elif level == "hard":
        lives = 1
    menu_frame.place_forget()
    
    score = 0
    speed_multiplier = 1.0
    running = True
    items.clear()
    
    canvas = tk.Canvas(root, width=500, height=700)
    canvas.pack()
    
    canvas.create_image(0, 0, image=bg_img, anchor="nw")
    score_display = canvas.create_text(80, 30, text=f"Score: {score}", font=("Arial", 16, "bold"), fill="white")
    lives_display = canvas.create_text(420, 30, text=f"Lives: {lives}", font=("Arial", 16, "bold"), fill="white")
    spawn_loop()
    game_loop()

def spawn_loop():
    if not running: return
    
    x = random.randint(50, 450)
    is_good = random.random() > 0.40
    img = good_img if is_good else bad_img
    
    item_id = canvas.create_image(x, -50, image=img, anchor="center")
    
    canvas.tag_bind(item_id, "<Button-1>", lambda e, i=item_id, g=is_good: process_click(i, g))
    items.append({"id": item_id, "is_good": is_good})
    
    interval = max(400, int(1200 / speed_multiplier))
    root.after(interval, spawn_loop)

def process_click(item_id, is_good):
    global score, speed_multiplier, items
    if not running: return
    
    if is_good:
        score += 15
        canvas.itemconfig(score_display, text=f"Score: {score}")
        if score % 10 == 0:
            speed_multiplier += 0.1
        canvas.delete(item_id)
        items = [i for i in items if i["id"] != item_id]
    else:
        if lives > 0:
            lives -= 1
            canvas.itemconfig(lives_display, text=f"Lives: {lives}")
            canvas.delete(item_id)
            items = [i for i in items if i["id"] != item_id]   
            if lives == 0:
                end_game()

def game_loop():
    global score, items
    if not running : return
    
    current_speed = 5 * speed_multiplier
    
    for item_data in items[:]:
        item = item_data["id"]
        canvas.move(item, 0, current_speed)
        
        coords = canvas.coords(item)
        if coords and coords[1] > 750: 
            if item_data["is_good"]:
                score = max(0, score - 10)
                canvas.itemconfig(score_display, text=f"Score: {score}")
            
            canvas.delete(item)
            if item_data in items:
                items.remove(item_data)

    root.after(30, game_loop)

def end_game():
    global running
    running = False
    end_gameframe = tk.Frame(root, bg="#F5DEB3")
    end_gameframe.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(end_gameframe, text="CROISSANT RUSH", font=("Courier", 30, "bold"), bg="#F5DEB3").pack(pady=50)
    tk.Label(end_gameframe, text=f"GAME OVER\nYour Score: {score}", font=("Arial", 18), bg="#F5DEB3").pack(pady=20)
    tk.Button(end_gameframe, text="PLAY AGAIN", font=("Arial", 18), command=lambda: [end_gameframe.destroy(), difficulty_selection], width=30).pack(pady=20)
    tk.Button(end_gameframe, text="BACK TO MENU", font=("Arial", 18), command=lambda: [end_gameframe.destroy(), show_menu()], width=30).pack(pady=20)
    tk.Button(end_gameframe, text="QUIT", font=("Arial", 18), command=root.quit, width=30).pack(pady=20)
    canvas.destroy()


# Initialisation de la fenêtre principale
root = tk.Tk()
root.title("Croissant Rush")
root.geometry("500x700")

# Chargement et redimensionnement des ressources
bg_img = ImageTk.PhotoImage(Image.open("pixelcafe.png").resize((500, 700)))
good_img = ImageTk.PhotoImage(Image.open("croissant.png").resize((60, 60)))
bad_img = ImageTk.PhotoImage(Image.open("pizzacroissant.png").resize((60, 60)))

show_menu()
root.mainloop()