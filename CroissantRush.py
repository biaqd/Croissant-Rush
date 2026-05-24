import tkinter as tk
import random
from PIL import Image, ImageTk, ImageColor
import json
import os
from datetime import datetime

# Variables globales
score = 0
lives = 0
speed_multiplier = 1.0
running = False
items = []
current_background_key = "default"

BACKGROUNDS = [
    {"id": "default", "name": "Classic", "unlock": 0, "start": "#CEA261", "end": "#8F7033"},
    {"id": "sunrise", "name": "Sunrise", "unlock": 60, "start": "#FFD580", "end": "#FF8E72"},
    {"id": "ocean", "name": "Ocean", "unlock": 100, "start": "#70C4FF", "end": "#205B9F"},
    {"id": "lavender", "name": "Lavender", "unlock": 140, "start": "#DCC6FF", "end": "#7A63FF"},
    {"id": "mint", "name": "Mint", "unlock": 200, "start": "#C6FFE3", "end": "#4EB48D"},
    {"id": "twilight", "name": "Twilight", "unlock": 260, "start": "#FFA8D8", "end": "#452A7A"},
    {"id": "coral", "name": "Coral", "unlock": 320, "start": "#FFB1A4", "end": "#FF5A3C"},
    {"id": "forest", "name": "Forest", "unlock": 400, "start": "#95D8A9", "end": "#1F5C36"},
    {"id": "night", "name": "Night", "unlock": 500, "start": "#171B3C", "end": "#5B218F"},
    {"id": "galaxy", "name": "Galaxy", "unlock": 1000, "start": "#2D2D72", "end": "#1B1B40"},
]

BACKGROUND_ORDER = [bg["id"] for bg in BACKGROUNDS]

def show_menu():
    global menu_frame
    menu_frame = tk.Frame(root, bg="#F5DEB3")
    menu_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(menu_frame, text="CROISSANT RUSH", font=("Courier", 30, "bold"), bg="#F5DEB3").pack(pady=50)
    tk.Button(menu_frame, text="PLAY", font=("Arial", 18), command=difficulty_selection, width=30).pack(pady=20)
    tk.Button(menu_frame, text="CREDITS", font=("Arial", 18), command=credits, width=30).pack(pady=20)
    tk.Button(menu_frame, text="SCOREBOARD", font=("Arial", 18), command=lambda: [menu_frame.destroy(), show_scoreboard()], width=30).pack(pady=20)
    tk.Button(menu_frame, text="BACKGROUNDS", font=("Arial", 18), command=lambda: [menu_frame.destroy(), show_background_panel()], width=30).pack(pady=20)
    tk.Button(menu_frame, text="QUIT", font=("Arial", 18), command=root.quit, width=30).pack(pady=20)

def credits():
    credits_frame = tk.Frame(root, bg="#F5DEB3")
    credits_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(credits_frame, text="CREDITS", font=("Courier", 24, "bold"), bg="#F5DEB3").pack(pady=20)
    tk.Label(credits_frame, text="Thank you for playing!\n\nthis game was inspired by arcade games :)\n\nDeveloped by Paris Baguette Team", font=("Arial", 18), bg="#F5DEB3").pack(pady=40)
    tk.Button(credits_frame, text="BACK TO MENU", font=("Arial", 18), command=lambda: [credits_frame.destroy(), show_menu()],width=30).pack(pady=60)


def difficulty_selection():
    difficulty_frame = tk.Frame(root, bg="#F5DEB3")
    difficulty_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(difficulty_frame, 
             text="SELECT DIFFICULTY", 
             font=("Courier", 24, "bold"), bg="#F5DEB3").pack(pady=50)
    tk.Button(difficulty_frame, 
              text="EASY (5 life)", 
              font=("Arial", 18),
              command=lambda: [difficulty_frame.destroy(), difficulty_selected("easy")], width=30).pack(pady=20)
    tk.Button(difficulty_frame, 
              text="MEDIUM (3 life)", 
              font=("Arial", 18),
              command=lambda: [difficulty_frame.destroy(), difficulty_selected("medium")], width=30).pack(pady=20)
    tk.Button(difficulty_frame,
               text="HARD (1 life)",
                 font=("Arial", 18), 
                 command=lambda: [difficulty_frame.destroy(), difficulty_selected("hard")], width=30).pack(pady=20)
    tk.Button(difficulty_frame, text="BACK", font=("Arial", 14), command=lambda: [difficulty_frame.destroy(), show_menu()], width=12).pack(pady=30)

def difficulty_selected(lvl):
    global level, lives
    level = lvl
    if level == "easy":
        lives = 5
    elif level == "medium":
        lives = 3
    elif level == "hard":
        lives = 1
    start_game()


    
def start_game():
    global score, speed_multiplier, running, items, canvas, score_display, lives_display, lives, level
    menu_frame.place_forget()
    
    score = 0
    speed_multiplier = 1.0
    running = True
    items.clear()
    
    canvas = tk.Canvas(root, width=500, height=700)
    canvas.pack()
    
    bg_image = bg_images.get(current_background_key, bg_images["default"])
    canvas.create_image(0, 0, image=bg_image, anchor="nw")
    score_display = canvas.create_text(80, 30, text=f"Score: {score}", font=("Arial", 16, "bold"), fill="white")
    # move lives below score to avoid overlap with pause button
    lives_display = canvas.create_text(80, 60, text=f"Lives: {lives}", font=("Arial", 14, "bold"), fill="white")
    spawn_loop()
    game_loop()
    # create a pause button on the canvas
    global pause_button, pause_button_window
    pause_button = tk.Button(root, text="PAUSE", font=("Arial", 12), command=pause_game)
    try:
        pause_button_window = canvas.create_window(420, 10, anchor="nw", window=pause_button)
    except Exception:
        pause_button_window = None

def spawn_loop():
    if not running: return
    
    x = random.randint(50, 450)
    is_good = random.random() > 0.30
    img = good_img if is_good else bad_img
    
    item_id = canvas.create_image(x, -50, image=img, anchor="center")
    
    canvas.tag_bind(item_id, "<Button-1>", lambda e, i=item_id, g=is_good: process_click(i, g))
    items.append({"id": item_id, "is_good": is_good})
    
    interval = max(400, int(1200 / speed_multiplier))
    root.after(interval, spawn_loop)

def process_click(item_id, is_good):
    global score, speed_multiplier, items, lives
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

    root.after(10, game_loop)


def get_scores_file():
    try:
        base = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        base = os.getcwd()
    return os.path.join(base, "high_score.json")


def load_data():
    path = get_scores_file()
    if not os.path.exists(path):
        return {"scores": [], "unlocked_backgrounds": ["default"], "selected_background": "default"}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"scores": data, "unlocked_backgrounds": ["default"], "selected_background": "default"}
            if isinstance(data, dict):
                return {
                    "scores": data.get("scores", []),
                    "unlocked_backgrounds": data.get("unlocked_backgrounds", ["default"]),
                    "selected_background": data.get("selected_background", "default"),
                }
    except Exception:
        pass
    return {"scores": [], "unlocked_backgrounds": ["default"], "selected_background": "default"}


def save_data(data):
    try:
        with open(get_scores_file(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Failed to save data:", e)


def load_scores():
    return load_data().get("scores", [])


def unlock_backgrounds(score, data):
    unlocked = set(data.get("unlocked_backgrounds", ["default"]))
    previous = set(unlocked)
    for bg in BACKGROUNDS:
        if score >= bg["unlock"]:
            unlocked.add(bg["id"])
    data["unlocked_backgrounds"] = [key for key in BACKGROUND_ORDER if key in unlocked]
    newly_unlocked = [bg["name"] for bg in BACKGROUNDS if bg["id"] in unlocked and bg["id"] not in previous]
    return data, newly_unlocked


def save_score(value):
    try:
        data = load_data()
        data["scores"].append({"score": int(value), "date": datetime.utcnow().isoformat()})
        data["scores"] = sorted(data["scores"], key=lambda x: x.get("score", 0), reverse=True)[:10]
        data, newly_unlocked = unlock_backgrounds(value, data)
        save_data(data)
        return newly_unlocked
    except Exception as e:
        print("Failed to save score:", e)
        return []


def select_background(key):
    global current_background_key
    data = load_data()
    if key in data.get("unlocked_backgrounds", []):
        current_background_key = key
        data["selected_background"] = key
        save_data(data)


def show_background_panel():
    board_frame = tk.Frame(root, bg="#F5DEB3")
    board_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Button(board_frame, text="BACK", font=("Arial", 12), command=lambda: [board_frame.destroy(), show_menu()]).pack(anchor="nw", padx=10, pady=10)
    tk.Label(board_frame, text="BACKGROUND UNLOCKS", font=("Courier", 24, "bold"), bg="#F5DEB3").pack(pady=20)
    data = load_data()
    unlocked = set(data.get("unlocked_backgrounds", ["default"]))
    best_score = max([entry.get("score", 0) for entry in data.get("scores", [])], default=0)
    tk.Label(board_frame, text=f"Best score: {best_score}", font=("Arial", 16), bg="#F5DEB3").pack(pady=10)

    def make_select(k):
        return lambda: [select_background(k), board_frame.destroy(), show_background_panel()]

    for bg in BACKGROUNDS:
        frame = tk.Frame(board_frame, bg="#F5DEB3")
        frame.pack(fill="x", pady=5, padx=20)
        status = "Unlocked" if bg["id"] in unlocked else f'Locked until {bg["unlock"]}'
        tk.Label(frame, text=f"{bg['name']}", font=("Arial", 16, "bold"), bg="#F5DEB3").pack(side="left")
        tk.Label(frame, text=status, font=("Arial", 14), bg="#F5DEB3").pack(side="left", padx=10)
        if bg["id"] in unlocked:
            if bg["id"] == current_background_key:
                tk.Button(frame, text="SELECTED", font=("Arial", 12), state="disabled").pack(side="right")
            else:
                tk.Button(frame, text="SELECT", font=("Arial", 12), command=make_select(bg["id"])).pack(side="right")
        else:
            tk.Button(frame, text="LOCKED", font=("Arial", 12), state="disabled").pack(side="right")
    tk.Button(board_frame, text="BACK TO MENU", font=("Arial", 18), command=lambda: [board_frame.destroy(), show_menu()], width=30).pack(pady=20)
    tk.Label(board_frame, text="Unlock new backgrounds by reaching high scores.", font=("Arial", 14), bg="#F5DEB3").pack(pady=10)


def show_scoreboard():
    board_frame = tk.Frame(root, bg="#F5DEB3")
    board_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Button(board_frame, text="BACK", font=("Arial", 12), command=lambda: [board_frame.destroy(), show_menu()]).pack(anchor="nw", padx=10, pady=10)
    tk.Label(board_frame, text="HIGH SCORES", font=("Courier", 24, "bold"), bg="#F5DEB3").pack(pady=20)
    data = load_data()
    scores = data.get("scores", [])
    if not scores:
        tk.Label(board_frame, text="No high scores yet.", font=("Arial", 16), bg="#F5DEB3").pack(pady=20)
    else:
        for i, entry in enumerate(scores, start=1):
            score_text = f"{i}. {entry.get('score', 0)} - {entry.get('date','')[:10]}"
            tk.Label(board_frame, text=score_text, font=("Arial", 16), bg="#F5DEB3").pack(pady=2)
    tk.Button(board_frame, text="BACK TO MENU", font=("Arial", 18), command=lambda: [board_frame.destroy(), show_menu()], width=30).pack(pady=30)


def pause_game():
    global running, pause_frame
    if not running:
        return
    running = False
    try:
        pause_button.config(state="disabled")
    except Exception:
        pass
    pause_frame = tk.Frame(root, bg="#000000", bd=2)
    pause_frame.place(relx=0.2, rely=0.25, relwidth=0.6, relheight=0.5)
    tk.Label(pause_frame, text="PAUSED", font=("Courier", 24, "bold"), bg="#000000", fg="white").pack(pady=20)
    tk.Button(pause_frame, text="RESUME", font=("Arial", 16), command=resume_game, width=20).pack(pady=10)
    tk.Button(pause_frame, text="QUIT TO MENU", font=("Arial", 16), command=quit_to_menu_from_pause, width=20).pack(pady=10)


def resume_game():
    global running
    try:
        pause_frame.destroy()
    except Exception:
        pass
    try:
        pause_button.config(state="normal")
    except Exception:
        pass
    running = True
    spawn_loop()
    game_loop()


def quit_to_menu_from_pause():
    global running
    try:
        pause_frame.destroy()
    except Exception:
        pass
    running = False
    try:
        canvas.destroy()
    except Exception:
        pass
    try:
        pause_button.destroy()
    except Exception:
        pass
    show_menu()

def end_game():
    global running
    running = False
    unlocked = []
    try:
        unlocked = save_score(score)
    except Exception:
        pass
    try:
        pause_button.destroy()
    except Exception:
        pass
    try:
        pause_frame.destroy()
    except Exception:
        pass
    end_gameframe = tk.Frame(root, bg="#F5DEB3")
    end_gameframe.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(end_gameframe, text="CROISSANT RUSH", font=("Courier", 30, "bold"), bg="#F5DEB3").pack(pady=50)
    tk.Label(end_gameframe, text=f" Thank you for playing! \n GAME OVER\nYour Score: {score}", font=("Arial", 18), bg="#F5DEB3").pack(pady=20)
    if unlocked:
        tk.Label(end_gameframe, text=f"New unlock: {', '.join(unlocked)}", font=("Arial", 16), bg="#F5DEB3", fg="#2E8B57").pack(pady=10)
    tk.Button(end_gameframe, text="PLAY AGAIN", font=("Arial", 18), command=difficulty_selection, width=30).pack(pady=20)
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


def make_gradient_image(start_hex, end_hex):
    start = ImageColor.getrgb(start_hex)
    end = ImageColor.getrgb(end_hex)
    raw = Image.new("RGB", (500, 700), start)
    for y in range(700):
        blend = y / 699
        r = int(start[0] * (1 - blend) + end[0] * blend)
        g = int(start[1] * (1 - blend) + end[1] * blend)
        b = int(start[2] * (1 - blend) + end[2] * blend)
        for x in range(500):
            raw.putpixel((x, y), (r, g, b))
    return ImageTk.PhotoImage(raw)

bg_images = {"default": bg_img}
for bg in BACKGROUNDS:
    if bg["id"] == "default":
        continue
    bg_images[bg["id"]] = make_gradient_image(bg["start"], bg["end"])

stored_data = load_data()
current_background_key = stored_data.get("selected_background", "default")

show_menu()
root.mainloop()

for y in range(700):
    blend = y / 700
    r = int(255 * (1 - blend) + 80 * blend)
    g = int(176 * (1 - blend) + 160 * blend)
    b = int(110 * (1 - blend) + 200 * blend)
    for x in range(500):
        sunset_raw.putpixel((x, y), (r, g, b))
sunset_img = ImageTk.PhotoImage(sunset_raw)

ocean_raw = Image.new("RGB", (500, 700), "#3080C0")
for y in range(700):
    blend = y / 700
    r = int(48 * (1 - blend) + 10 * blend)
    g = int(128 * (1 - blend) + 40 * blend)
    b = int(192 * (1 - blend) + 100 * blend)
    for x in range(500):
        ocean_raw.putpixel((x, y), (r, g, b))
ocean_img = ImageTk.PhotoImage(ocean_raw)

bg_images = {
    "default": bg_img,
    "sunset": sunset_img,
    "ocean": ocean_img,
}

stored_data = load_data()
current_background_key = stored_data.get("selected_background", "default")

show_menu()
root.mainloop()