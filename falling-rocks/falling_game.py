import pygame
import pymunk
import sqlite3
import tkinter as tk
from tkinter import simpledialog
from random import randint
from rich.console import Console
import os

# Setup
pygame.init()
pygame.mixer.init()

# Background music
if os.path.exists("falling-rocks/background.wav"):
    pygame.mixer.music.load("falling-rocks/background.wav")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
else:
    print("⚠️ background.wav not found.")

WIDTH, HEIGHT = 600, 700
PLAYER_SIZE = 64
ROCK_SIZE = 30
GRAVITY = 900
FPS = 60

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🪨 Falling Rocks Dodge")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)

WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLACK = (0, 0, 0)

space = pymunk.Space()
space.gravity = (0, GRAVITY)

# Load Player
if not os.path.exists("falling-rocks\player.png"):
    raise FileNotFoundError("❌ player.png not found.")
player_img = pygame.image.load("falling-rocks\player.png")
player_img = pygame.transform.scale(player_img, (PLAYER_SIZE, PLAYER_SIZE))
player = pygame.Rect(WIDTH // 2, HEIGHT - 80, PLAYER_SIZE, PLAYER_SIZE)

# Load Death Sound
if os.path.exists("falling-rocks\death_sound.wav"):
    hit_sound = pygame.mixer.Sound("falling-rocks\death_sound.wav")
    hit_sound.set_volume(1.0)
else:
    hit_sound = None
    print("⚠️ death_sound.wav not found.")

# Rock Setup
rocks = []
def add_rock():
    body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, ROCK_SIZE))
    body.position = (randint(0, WIDTH - ROCK_SIZE), -ROCK_SIZE)
    shape = pymunk.Circle(body, ROCK_SIZE)
    shape.elasticity = 0
    space.add(body, shape)
    return shape

# Game loop
console = Console()
spawn_timer = 0
score = 0
frame_counter = 0
run = True
while run:
    win.fill(WHITE)
    dt = clock.tick(FPS) / 1000
    space.step(dt)
    frame_counter += 1
    if frame_counter % 6 == 0:
        score += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.x -= 5
    if keys[pygame.K_RIGHT]: player.x += 5
    player.x = max(0, min(WIDTH - PLAYER_SIZE, player.x))

    win.blit(player_img, player)

    spawn_timer += 1
    if spawn_timer > 30:
        rocks.append(add_rock())
        spawn_timer = 0

    for rock in rocks:
        x, y = rock.body.position
        pygame.draw.circle(win, RED, (int(x), int(y)), ROCK_SIZE)

        if player.collidepoint(int(x), int(y)):
            if hit_sound:
                hit_sound.play()
                pygame.time.wait(int(hit_sound.get_length() * 1000))
            pygame.quit()

            # Ask username
            root = tk.Tk()
            root.withdraw()
            username = simpledialog.askstring("Game Over", "Enter your name:")

            if username:
                # Save to SQLite
                conn = sqlite3.connect("leaderboard.db")
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        score INTEGER NOT NULL
                    )
                """)
                conn.commit()
                cursor.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (username, score))
                conn.commit()

                # Show Top 10
                cursor.execute("SELECT username, score FROM scores ORDER BY score DESC LIMIT 10")
                top_scores = cursor.fetchall()
                conn.close()

                print("\n🏆 Top 10 Scores:")
                for i, (name, scr) in enumerate(top_scores, 1):
                    print(f"{i}. {name} - {scr}")
            else:
                print("No name entered. Score not saved.")
            exit()

    # Draw score
    score_surface = font.render(f"Score: {score}", True, BLACK)
    win.blit(score_surface, (10, 10))

    pygame.display.update()
