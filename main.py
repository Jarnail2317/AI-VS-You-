import pygame
import sys
import random

pygame.init()

# Fenster
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake 3‑Player (2 lernende KIs + Du)")

# Farben
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
BLUE = (50, 150, 255)
DARK_BLUE = (30, 100, 200)
PURPLE = (180, 0, 180)
DARK_PURPLE = (120, 0, 120)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
PINK = (255, 100, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)

font = pygame.font.SysFont("Arial", 25)
big_font = pygame.font.SysFont("Arial", 50)

clock = pygame.time.Clock()
snake_speed = 12

# "Lernende" Parameter der KIs (zwischen 0 und 1)
# cautious = 0 -> sehr riskant, cautious = 1 -> sehr vorsichtig
ai_memory = {
    "green": {"cautious": 0.5},
    "blue": {"cautious": 0.5}
}


def draw_text(text, font, color, x, y):
    screen.blit(font.render(text, True, color), (x, y))


def start_menu():
    while True:
        screen.fill(BLACK)
        draw_text("SNAKE 3‑PLAYER", big_font, GREEN, 140, 100)
        draw_text("2 lernende KIs + DU spielst selbst", font, WHITE, 130, 180)
        draw_text("ENTER = Start", font, WHITE, 230, 240)
        draw_text("ESC = Beenden", font, WHITE, 230, 280)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def ai_move(snake_pos, food_pos, direction, enemies, cautious):
    """
    Einfache KI:
    - versucht Richtung Essen zu gehen
    - vermeidet Gegner
    - je nach 'cautious' nimmt sie eher sichere oder riskante Züge
    """
    dx = food_pos[0] - snake_pos[0]
    dy = food_pos[1] - snake_pos[1]

    options = ["UP", "DOWN", "LEFT", "RIGHT"]
    preferred = []

    if dx > 0:
        preferred.append("RIGHT")
    if dx < 0:
        preferred.append("LEFT")
    if dy > 0:
        preferred.append("DOWN")
    if dy < 0:
        preferred.append("UP")

    safe = []
    unsafe_preferred = []

    for move in options:
        nx, ny = snake_pos[0], snake_pos[1]

        if move == "UP":
            ny -= 10
        if move == "DOWN":
            ny += 10
        if move == "LEFT":
            nx -= 10
        if move == "RIGHT":
            nx += 10

        next_pos = [nx, ny]

        if next_pos in enemies:
            # Zug führt in Gegner -> unsicher
            if move in preferred:
                unsafe_preferred.append(move)
        else:
            # sicherer Zug
            safe.append(move)

    # 1. Bevorzugte sichere Richtung
    for move in preferred:
        if move in safe:
            return move

    # 2. Riskante bevorzugte Richtung mit Wahrscheinlichkeit abhängig von cautious
    # cautious hoch -> selten riskant, cautious niedrig -> oft riskant
    if unsafe_preferred:
        import random as rnd
        risk_prob = max(0.1, 1.0 - cautious)  # 0.1 bis 0.9
        if rnd.random() < risk_prob:
            return rnd.choice(unsafe_preferred)

    # 3. Irgendein sicherer Zug
    if safe:
        import random as rnd
        return rnd.choice(safe)

    # 4. Wenn gar nichts geht -> bleib in Bewegung
    return direction


def spawn_food():
    return [random.randrange(1, 60) * 10, random.randrange(1, 40) * 10]


def game_loop():
    # KI Grün
    s1_pos = [100, 50]
    s1_body = [[100, 50], [90, 50], [80, 50]]
    d1 = "RIGHT"

    # KI Blau
    s2_pos = [500, 350]
    s2_body = [[500, 350], [510, 350], [520, 350]]
    d2 = "LEFT"

    # Spieler Lila
    s3_pos = [300, 200]
    s3_body = [[300, 200], [290, 200], [280, 200]]
    d3 = "RIGHT"

    # Essen
    f1 = spawn_food()
    f2 = spawn_food()
    f3 = spawn_food()

    alive1 = alive2 = alive3 = True

    score1 = score2 = score3 = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Spielersteuerung (WASD)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and d3 != "DOWN":
                    d3 = "UP"
                if event.key == pygame.K_s and d3 != "UP":
                    d3 = "DOWN"
                if event.key == pygame.K_a and d3 != "RIGHT":
                    d3 = "LEFT"
                if event.key == pygame.K_d and d3 != "LEFT":
                    d3 = "RIGHT"

        # KI Entscheidungen mit "lernenden" cautious-Werten
        if alive1:
            d1 = ai_move(
                s1_pos,
                f1,
                d1,
                enemies=s2_body + s3_body,
                cautious=ai_memory["green"]["cautious"]
            )
        if alive2:
            d2 = ai_move(
                s2_pos,
                f2,
                d2,
                enemies=s1_body + s3_body,
                cautious=ai_memory["blue"]["cautious"]
            )

        # Bewegung
        def move(pos, direction):
            if direction == "UP":
                pos[1] -= 10
            if direction == "DOWN":
                pos[1] += 10
            if direction == "LEFT":
                pos[0] -= 10
            if direction == "RIGHT":
                pos[0] += 10

        if alive1:
            move(s1_pos, d1)
        if alive2:
            move(s2_pos, d2)
        if alive3:
            move(s3_pos, d3)

        # Körper aktualisieren
        if alive1:
            s1_body.insert(0, list(s1_pos))
        if alive2:
            s2_body.insert(0, list(s2_pos))
        if alive3:
            s3_body.insert(0, list(s3_pos))

        # Essen
        if alive1 and s1_pos == f1:
            score1 += 1
            f1 = spawn_food()
        else:
            if alive1:
                s1_body.pop()

        if alive2 and s2_pos == f2:
            score2 += 1
            f2 = spawn_food()
        else:
            if alive2:
                s2_body.pop()

        if alive3 and s3_pos == f3:
            score3 += 1
            f3 = spawn_food()
        else:
            if alive3:
                s3_body.pop()

        screen.fill(GRAY)

        # Zeichnen
        for i, b in enumerate(s1_body):
            pygame.draw.rect(screen, GREEN if i == 0 else DARK_GREEN, (b[0], b[1], 10, 10))

        for i, b in enumerate(s2_body):
            pygame.draw.rect(screen, BLUE if i == 0 else DARK_BLUE, (b[0], b[1], 10, 10))

        for i, b in enumerate(s3_body):
            pygame.draw.rect(screen, PURPLE if i == 0 else DARK_PURPLE, (b[0], b[1], 10, 10))

        pygame.draw.rect(screen, RED, (f1[0], f1[1], 10, 10))
        pygame.draw.rect(screen, YELLOW, (f2[0], f2[1], 10, 10))
        pygame.draw.rect(screen, PINK, (f3[0], f3[1], 10, 10))

        # Kollisionen
        def dead(pos, body, enemies):
            return (
                pos[0] < 0 or pos[0] > WIDTH - 10 or
                pos[1] < 0 or pos[1] > HEIGHT - 10 or
                pos in body[1:] or
                pos in enemies
            )

        if alive1 and dead(s1_pos, s1_body, s2_body + s3_body):
            alive1 = False
        if alive2 and dead(s2_pos, s2_body, s1_body + s3_body):
            alive2 = False
        if alive3 and dead(s3_pos, s3_body, s1_body + s2_body):
            alive3 = False

        # Gewinner bestimmen
        alive_count = alive1 + alive2 + alive3
        if alive_count <= 1:
            if alive1:
                winner = "Grün gewinnt!"
            elif alive2:
                winner = "Blau gewinnt!"
            elif alive3:
                winner = "Du gewinnst!"
            else:
                winner = "Unentschieden"

            return winner, score1, score2, score3

        # Punkte + aktuelle cautious-Werte anzeigen
        draw_text(f"Grün: {score1}  (cautious={ai_memory['green']['cautious']:.2f})", font, WHITE, 10, 10)
        draw_text(f"Blau: {score2}  (cautious={ai_memory['blue']['cautious']:.2f})", font, WHITE, 10, 40)
        draw_text(f"Du: {score3}", font, WHITE, 500, 10)

        pygame.display.update()
        clock.tick(snake_speed)


def update_ai_learning(winner):
    """
    Einfaches "Lernen":
    - Gewinner-KI wird etwas aggressiver (cautious runter)
    - Verlierer-KI wird etwas vorsichtiger (cautious rauf)
    - Wenn du gewinnst, werden beide KIs vorsichtiger
    """
    step = 0.05

    if winner == "Grün gewinnt!":
        ai_memory["green"]["cautious"] = max(0.05, ai_memory["green"]["cautious"] - step)
        ai_memory["blue"]["cautious"] = min(0.95, ai_memory["blue"]["cautious"] + step)
    elif winner == "Blau gewinnt!":
        ai_memory["blue"]["cautious"] = max(0.05, ai_memory["blue"]["cautious"] - step)
        ai_memory["green"]["cautious"] = min(0.95, ai_memory["green"]["cautious"] + step)
    elif winner == "Du gewinnst!":
        ai_memory["green"]["cautious"] = min(0.95, ai_memory["green"]["cautious"] + step)
        ai_memory["blue"]["cautious"] = min(0.95, ai_memory["blue"]["cautious"] + step)
    # Unentschieden -> keine Änderung


def game_over_screen(winner, s1, s2, s3):
    while True:
        screen.fill(BLACK)
        draw_text(winner, big_font, RED, 150, 100)
        draw_text(f"Grün: {s1}  |  Blau: {s2}  |  Du: {s3}", font, WHITE, 150, 180)
        draw_text("ENTER = Neustart", font, GREEN, 210, 240)
        draw_text("ESC = Beenden", font, GREEN, 230, 270)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


start_menu()

while True:
    winner, s1, s2, s3 = game_loop()
    update_ai_learning(winner)  # hier "lernen" die KIs über Runden
    game_over_screen(winner, s1, s2, s3)
