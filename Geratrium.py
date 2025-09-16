
# geratrium_final.py

import pygame
import sys
import random
import math
from typing import List, Optional, Tuple
from collections import deque

# ---- Init ----
pygame.init()
pygame.font.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)  # borderless fullscreen
pygame.display.set_caption("Geratrix")
CLOCK = pygame.time.Clock()
FPS = 60

# ---- Colors ----
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)

BLUE = (0, 120, 255)
RED = (220, 50, 50)
GREEN = (40, 200, 80)
YELLOW = (255, 215, 0)
PANEL_BLUE = (10, 10, 40)
PANEL_RED = (40, 10, 10)

# ---- Fonts ----
FONT_SMALL = pygame.font.SysFont("Times New Roman", 22)
FONT = pygame.font.SysFont("Times New Roman", 30)
MENU_FONT = pygame.font.SysFont("Times New Roman", 64, bold=True)
TITLE_FONT = pygame.font.SysFont("Times New Roman", 144, bold=True)
RULES_FONT = pygame.font.SysFont("Times New Roman", 26)
CREDIT_FONT = pygame.font.SysFont("Times New Roman", 28, italic=True)

# ---- Directions ----
DIRS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}
KEY_LIST = list(DIRS.values())  # used consistently for neighbor iteration

KEYS_P1 = {pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT"}
KEYS_P2 = {pygame.K_w: "UP", pygame.K_s: "DOWN", pygame.K_a: "LEFT", pygame.K_d: "RIGHT"}

# ---- Rules (final provided) ----
RULES_TEXT = [
    "Regra 1: O jogo é uma MD5, o jogador que ganhar 3 tabuleiros primeiro ganha o jogo.",
    "Regra 2: Os tabuleiros de cada rodada terão, de forma aleatória, uma quantidade entre 7 e 11 de linhas e colunas.",
    "Regra 3: O primeiro jogador escolhe um quadriculado aleatório para começar, exceto o quadriculado central (se houver).",
    "Regra 4: O primeiro quadriculado do segundo jogador será aquele simétrico em relação ao centro do quadriculado do jogador 1.",
    "Regra 5: Os jogadores jogarão de forma alternada.",
    "Regra 6: Um quadriculado não pode ser utilizado duas vezes.",
    "Regra 7: Em cada rodada, o jogador poderá escolher o quadriculado da direita, da esquerda, em cima ou embaixo do atual.",
    "Regra 8: O jogador que não conseguir mais mexer primeiro perde a rodada.",
    "Regra 9: Have Fun!"
]

# ---- Utilities ----
def render_text_gradient(text: str, font: pygame.font.Font, top_color: Tuple[int,int,int], bottom_color: Tuple[int,int,int]) -> pygame.Surface:
    text_surf = font.render(text, True, WHITE).convert_alpha()
    w, h = text_surf.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        pygame.draw.line(grad, (r, g, b, 255), (0, y), (w, y))
    grad.blit(text_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return grad

def draw_centered(surface: pygame.Surface, surf: pygame.Surface, center_y: int):
    rect = surf.get_rect(center=(WIDTH // 2, center_y))
    surface.blit(surf, rect)

def wait_responsive(ms: int):
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < ms:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        CLOCK.tick(FPS)

# ---- Board helpers ----
def criar_tabuleiro() -> List[List[Optional[int]]]:
    linhas = random.randint(7, 11)
    colunas = random.randint(7, 11)
    return [[None for _ in range(colunas)] for _ in range(linhas)]

def posicao_simetrica(pos: Tuple[int,int], tabuleiro: List[List[Optional[int]]]) -> Optional[Tuple[int,int]]:
    rows = len(tabuleiro)
    cols = len(tabuleiro[0])
    centro_r = (rows - 1) / 2.0
    centro_c = (cols - 1) / 2.0
    sim_r = int(round(2 * centro_r - pos[0]))
    sim_c = int(round(2 * centro_c - pos[1]))
    if 0 <= sim_r < rows and 0 <= sim_c < cols:
        return (sim_r, sim_c)
    return None

def jogada_valida(tabuleiro: List[List[Optional[int]]], mov: Tuple[int,int]) -> bool:
    r, c = mov
    return 0 <= r < len(tabuleiro) and 0 <= c < len(tabuleiro[0]) and tabuleiro[r][c] is None

def obter_proxima_pos(pos: Tuple[int,int], direcao: str) -> Tuple[int,int]:
    dr, dc = DIRS[direcao]
    return pos[0] + dr, pos[1] + dc

# ---- Menus ----
def selecionar_dificuldade() -> Optional[int]:
    while True:
        SCREEN.fill(BLACK)
        title = TITLE_FONT.render("Escolha Dificuldade", True, WHITE)
        SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//6))

        opts = ["Easy (1)", "Medium (2)", "Hard (3)"]
        rects = []
        for i, txt in enumerate(opts):
            col = BLUE if i == 0 else (YELLOW if i == 1 else RED)
            surf = MENU_FONT.render(txt, True, col)
            rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 60 + i*120))
            SCREEN.blit(surf, rect)
            rects.append(rect)
        inst = FONT_SMALL.render("Pressione ESC para voltar", True, WHITE)
        SCREEN.blit(inst, (60, HEIGHT-60))
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                if ev.key == pygame.K_1:
                    return 0
                if ev.key == pygame.K_2:
                    return 1
                if ev.key == pygame.K_3:
                    return 2
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                for i, r in enumerate(rects):
                    if r.collidepoint(mx, my):
                        return i
        CLOCK.tick(FPS)

def menu_inicial() -> Optional[Tuple[bool, Optional[int]]]:
    while True:
        SCREEN.fill(BLACK)
        title_surf = render_text_gradient("Geratrix", TITLE_FONT, (200,160,255), (220,200,255))
        draw_centered(SCREEN, title_surf, HEIGHT//6)

        opt1 = MENU_FONT.render("Player 1 vs Player 2 (1)", True, BLUE)
        opt2 = MENU_FONT.render("Player 1 vs Bot (2)", True, RED)
        opt3 = MENU_FONT.render("Regras (3)", True, GREEN)

        opt1_rect = opt1.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
        opt2_rect = opt2.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
        opt3_rect = opt3.get_rect(center=(WIDTH//2, HEIGHT//2 + 200))

        SCREEN.blit(opt1, opt1_rect)
        SCREEN.blit(opt2, opt2_rect)
        SCREEN.blit(opt3, opt3_rect)

        # credit text below "Regras"
        credit_surf = CREDIT_FONT.render("By Caio Temponi", True, WHITE)
        credit_x = WIDTH//2 - credit_surf.get_width()//2
        credit_y = opt3_rect.y + opt3_rect.height + 100
        SCREEN.blit(credit_surf, (credit_x, credit_y))

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    return (False, None)
                if ev.key == pygame.K_2:
                    lvl = selecionar_dificuldade()
                    if lvl is None:
                        continue
                    return (True, lvl)
                if ev.key == pygame.K_3:
                    return "RULES"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if opt1_rect.collidepoint(mx, my):
                    return (False, None)
                if opt2_rect.collidepoint(mx, my):
                    lvl = selecionar_dificuldade()
                    if lvl is None:
                        continue
                    return (True, lvl)
                if opt3_rect.collidepoint(mx, my):
                    return "RULES"
        CLOCK.tick(FPS)

def mostrar_regras_page():
    while True:
        SCREEN.fill(BLACK)
        title = TITLE_FONT.render("Regras", True, WHITE)
        SCREEN.blit(title, (50, 30))
        y = 30 + title.get_height() + 30
        for regra in RULES_TEXT:
            surf = RULES_FONT.render(regra, True, WHITE)
            SCREEN.blit(surf, (60, y))
            y += RULES_FONT.get_height() + 18
        instr = FONT_SMALL.render("Pressione ESC para voltar", True, WHITE)
        SCREEN.blit(instr, (60, HEIGHT - 60))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return
        CLOCK.tick(FPS)

# ---- Drawing the board and UI ----
def desenhar_tabuleiro(tabuleiro: List[List[Optional[int]]],
                      posicoes: List[Optional[Tuple[int,int]]],
                      score: Tuple[int,int],
                      vs_bot: bool,
                      turno: int) -> Tuple[pygame.Rect, Tuple[int,int,int]]:
    SCREEN.fill(BLACK)
    rows = len(tabuleiro)
    cols = len(tabuleiro[0])
    margin = 60
    tile_size = min((WIDTH - 2*margin) // cols, (HEIGHT - 200) // rows)
    offset_x = (WIDTH - cols*tile_size) // 2
    offset_y = (HEIGHT - rows*tile_size) // 2

    # side panels
    pygame.draw.rect(SCREEN, PANEL_BLUE, (0, 0, offset_x, HEIGHT))
    pygame.draw.rect(SCREEN, PANEL_RED, (WIDTH - offset_x, 0, offset_x, HEIGHT))

    # scoreboard
    score_text = f"P1: {score[0]}   P2: {score[1]}" if not vs_bot else f"You: {score[0]}   Bot: {score[1]}"
    score_surf = FONT.render(score_text, True, WHITE)
    SCREEN.blit(score_surf, (WIDTH//2 - score_surf.get_width()//2, 20))

    # board border colored by current turn (subtle)
    borda_cor = BLUE if turno == 0 else RED
    pygame.draw.rect(SCREEN, borda_cor, (offset_x-6, offset_y-6, cols*tile_size+12, rows*tile_size+12), 6)

    # draw cells
    for r in range(rows):
        for c in range(cols):
            x = offset_x + c*tile_size
            y = offset_y + r*tile_size
            if tabuleiro[r][c] is None:
                cell_color = GRAY
            elif tabuleiro[r][c] == 0:
                cell_color = BLUE
            else:
                cell_color = RED
            pygame.draw.rect(SCREEN, cell_color, (x, y, tile_size-2, tile_size-2))

    # glowing border around current squares (pulsing)
    t = pygame.time.get_ticks() / 300.0
    factor = (math.sin(t) + 1) / 2.0  # 0..1
    glow_amp = 70
    base_thickness = 4
    thickness = base_thickness + int(3 * factor)
    for idx, pos in enumerate(posicoes):
        if pos is None:
            continue
        pr, pc = pos
        px = offset_x + pc*tile_size
        py = offset_y + pr*tile_size
        base_color = BLUE if idx == 0 else RED
        glow_color = tuple(min(255, int(base_color[i] + glow_amp * factor)) for i in range(3))
        pygame.draw.rect(SCREEN, glow_color, (px-3, py-3, tile_size+6, tile_size+6), thickness)

    # gear icon (rodinha) top-left
    gear_size = 46
    gear_margin = 12
    gear_x = gear_margin
    gear_y = gear_margin
    gear_cx = gear_x + gear_size//2
    gear_cy = gear_y + gear_size//2
    pygame.draw.circle(SCREEN, (80,80,80), (gear_cx, gear_cy), gear_size//2)
    for a in range(6):
        ang = a * (2*math.pi/6)
        ox = int(gear_cx + math.cos(ang)*(gear_size//2))
        oy = int(gear_cy + math.sin(ang)*(gear_size//2))
        ix = int(gear_cx + math.cos(ang)*(gear_size//4))
        iy = int(gear_cy + math.sin(ang)*(gear_size//4))
        pygame.draw.line(SCREEN, (200,200,200), (ix, iy), (ox, oy), 3)
    pygame.draw.circle(SCREEN, (30,30,30), (gear_cx, gear_cy), gear_size//4)
    gear_rect = pygame.Rect(gear_x, gear_y, gear_size, gear_size)

    return gear_rect, (offset_x, offset_y, tile_size)

# ---- Pause menu with automatic panel sizing and red pulsing borders ----
def draw_pause_option_rects_dynamic(option_x: int, option_y0: int, option_w: int, option_h: int,
                                    opts: List[str]) -> List[pygame.Rect]:
    rects: List[pygame.Rect] = []

    t = pygame.time.get_ticks() / 400.0
    pulse = (math.sin(t) + 1.0) / 2.0  # 0..1

    base = (180, 10, 10)
    bright = (255, 90, 90)
    borda_cor_menu = tuple(int(base[i] * (1 - pulse) + bright[i] * pulse) for i in range(3))
    thickness = 2 + int(3 * pulse)

    spacing = 28
    for i, txt in enumerate(opts):
        rect = pygame.Rect(option_x, option_y0 + i * (option_h + spacing), option_w, option_h)
        pygame.draw.rect(SCREEN, (50,50,50), rect, border_radius=10)
        pygame.draw.rect(SCREEN, borda_cor_menu, rect, thickness, border_radius=10)
        label = FONT.render(txt, True, WHITE)
        SCREEN.blit(label, (rect.x + rect.w//2 - label.get_width()//2, rect.y + rect.h//2 - label.get_height()//2))
        rects.append(rect)
    return rects

def desenhar_pausa_and_get_rects_dynamic(opts: List[str]) -> Tuple[List[pygame.Rect], Tuple[int,int,int,int]]:
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,160))
    SCREEN.blit(overlay, (0,0))

    label_surfs = [FONT.render(s, True, WHITE) for s in opts]
    label_widths = [s.get_width() for s in label_surfs]
    label_heights = [s.get_height() for s in label_surfs]

    option_w = max(label_widths) + 80
    option_h = max(label_heights) + 26

    spacing = 28
    panel_padding = 40
    panel_w = option_w + 2 * panel_padding
    panel_h = (option_h * len(opts)) + (spacing * (len(opts)-1)) + panel_padding*2 + 60
    panel_x = WIDTH//2 - panel_w//2
    panel_y = HEIGHT//2 - panel_h//2

    pygame.draw.rect(SCREEN, (24,24,24), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
    pygame.draw.rect(SCREEN, WHITE, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=12)

    title_surf = TITLE_FONT.render("Configurações", True, WHITE)
    SCREEN.blit(title_surf, (panel_x + panel_w//2 - title_surf.get_width()//2, panel_y - 200))

    option_x = panel_x + (panel_w - option_w)//2
    option_y0 = panel_y + 80

    rects = draw_pause_option_rects_dynamic(option_x, option_y0, option_w, option_h, opts)
    pygame.display.flip()
    panel_rect = (panel_x, panel_y, panel_w, panel_h)
    return rects, panel_rect

# ---- Animation message ----
def animar_mensagem(text: str, color: Tuple[int,int,int], duration_s: float = 0.9):
    frames = int(duration_s * FPS)
    for _ in range(frames):
        SCREEN.fill(BLACK)
        surf = TITLE_FONT.render(text, True, color)
        SCREEN.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2 - surf.get_height()//2))
        pygame.display.flip()
        CLOCK.tick(FPS)

# ---- Start-position selection ----
def selecionar_inicio(tabuleiro: List[List[Optional[int]]], bloqueado: Optional[Tuple[int,int]] = None) -> Tuple[int,int]:
    rows = len(tabuleiro)
    cols = len(tabuleiro[0])
    while True:
        gear_rect, draw_info = desenhar_tabuleiro(tabuleiro, [None, None], (0,0), False, 0)
        offset_x, offset_y, tile_size = draw_info
        instr = FONT.render("Clique para escolher a posição inicial (não clique no central se existir)", True, WHITE)
        SCREEN.blit(instr, (WIDTH//2 - instr.get_width()//2, 40))
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                for r in range(rows):
                    for c in range(cols):
                        x = offset_x + c*tile_size
                        y = offset_y + r*tile_size
                        if x <= mx <= x + tile_size and y <= my <= y + tile_size:
                            if bloqueado and (r,c) == bloqueado:
                                continue
                            return (r, c)
        CLOCK.tick(FPS)

# ---- Bot helpers ----
def count_reachable(tabuleiro: List[List[Optional[int]]], start: Tuple[int,int]) -> int:
    rows = len(tabuleiro)
    cols = len(tabuleiro[0])
    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        return 0
    if tabuleiro[start[0]][start[1]] is not None:
        return 0
    visited = [[False]*cols for _ in range(rows)]
    q = deque()
    q.append(start)
    visited[start[0]][start[1]] = True
    cnt = 0
    while q:
        r,c = q.popleft()
        cnt += 1
        for dr, dc in KEY_LIST:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and tabuleiro[nr][nc] is None:
                visited[nr][nc] = True
                q.append((nr,nc))
    return cnt

def bot_choose_move_easy(tabuleiro, pos):
    moves = list(KEY_LIST)
    random.shuffle(moves)
    for dr, dc in moves:
        nr, nc = pos[0] + dr, pos[1] + dc
        if jogada_valida(tabuleiro, (nr, nc)):
            return (nr, nc)
    return None

def bot_choose_move_medium(tabuleiro, pos):
    valid_moves = []
    for dr, dc in KEY_LIST:
        nr, nc = pos[0] + dr, pos[1] + dc
        if jogada_valida(tabuleiro, (nr, nc)):
            valid_moves.append((nr, nc))
    if not valid_moves:
        return None
    if random.random() < 0.66:
        best = None
        best_score = -1
        for nr, nc in valid_moves:
            tabuleiro[nr][nc] = 1
            score = count_reachable(tabuleiro, (nr, nc))
            tabuleiro[nr][nc] = None
            if score > best_score:
                best_score = score
                best = (nr, nc)
        return best
    else:
        return random.choice(valid_moves)

WEIGHTS = {'evitar_preso': 1.0, 'encurralar': 0.7, 'espelhar': 0.3}

# ANTI-COPYRIGHT LINE: Arthur Ribeiro Tavares

def bot_choose_move_hard(tabuleiro, own_pos, enemy_pos, last_player_move: Optional[Tuple[int,int]]):
    valid_moves = []
    for dr, dc in KEY_LIST:
        nr, nc = own_pos[0] + dr, own_pos[1] + dc
        if jogada_valida(tabuleiro, (nr, nc)):
            valid_moves.append((nr, nc))
    if not valid_moves:
        return None

    best = None
    best_score = -float('inf')

    mirror_target = None
    if last_player_move is not None:
        dr, dc = last_player_move
        mirror = (-dr, -dc)
        mirror_target = (own_pos[0] + mirror[0], own_pos[1] + mirror[1])
        if not (0 <= mirror_target[0] < len(tabuleiro) and 0 <= mirror_target[1] < len(tabuleiro[0])) or tabuleiro[mirror_target[0]][mirror_target[1]] is not None:
            mirror_target = None

    for (nr, nc) in valid_moves:
        tabuleiro[nr][nc] = 1

        own_future = 0
        for dr2, dc2 in KEY_LIST:
            r2, c2 = nr + dr2, nc + dc2
            if 0 <= r2 < len(tabuleiro) and 0 <= c2 < len(tabuleiro[0]) and tabuleiro[r2][c2] is None:
                own_future += 1
        if own_future == 0:
            own_future_penalty = -1000
        else:
            own_future_penalty = own_future

        opp_moves = 0
        for dr2, dc2 in KEY_LIST:
            orr, oc = enemy_pos[0] + dr2, enemy_pos[1] + dc2
            if 0 <= orr < len(tabuleiro) and 0 <= oc < len(tabuleiro[0]) and tabuleiro[orr][oc] is None:
                opp_moves += 1

        reach = count_reachable(tabuleiro, (nr, nc))

        mirror_bonus = 0
        if mirror_target is not None and (nr, nc) == mirror_target:
            mirror_bonus = 1

        score = 0.0
        score += WEIGHTS['evitar_preso'] * own_future_penalty
        score += WEIGHTS['encurralar'] * (-1.0 * opp_moves)
        score += 0.5 * reach
        score += WEIGHTS['espelhar'] * mirror_bonus * 5.0

        tabuleiro[nr][nc] = None

        if score > best_score:
            best_score = score
            best = (nr, nc)

    if best is None:
        return bot_choose_move_medium(tabuleiro, own_pos)
    return best

# ---- Round logic ----
def jogar_round(vs_bot: bool, score: List[int], bot_level: Optional[int] = None) -> Optional[int]:
    tabuleiro = criar_tabuleiro()
    rows, cols = len(tabuleiro), len(tabuleiro[0])

    centro_pos = None
    if rows % 2 == 1 and cols % 2 == 1:
        centro_pos = (rows//2, cols//2)

    p1_pos = selecionar_inicio(tabuleiro, bloqueado=centro_pos)
    tabuleiro[p1_pos[0]][p1_pos[1]] = 0

    p2_pos = posicao_simetrica(p1_pos, tabuleiro)
    if p2_pos and tabuleiro[p2_pos[0]][p2_pos[1]] is None:
        pass
    else:
        if vs_bot:
            choices = [(r,c) for r in range(rows) for c in range(cols) if tabuleiro[r][c] is None and (r,c) != p1_pos]
            p2_pos = random.choice(choices)
        else:
            p2_pos = selecionar_inicio(tabuleiro, bloqueado=p1_pos)
    tabuleiro[p2_pos[0]][p2_pos[1]] = 1

    pos = [p1_pos, p2_pos]
    turno = 0
    keys = [KEYS_P1, KEYS_P2]

    bot_timer = None
    paused = False
    gear_rect = None
    last_player_move: Optional[Tuple[int,int]] = None

    while True:
        gear_rect, draw_info = desenhar_tabuleiro(tabuleiro, pos, (score[0], score[1]), vs_bot, turno)
        pygame.display.flip()

        if vs_bot and turno == 1 and not paused:
            if bot_timer is None:
                bot_timer = pygame.time.get_ticks()
            else:
                if pygame.time.get_ticks() - bot_timer >= 500:
                    chosen = None
                    if bot_level == 0:
                        chosen = bot_choose_move_easy(tabuleiro, pos[1])
                    elif bot_level == 1:
                        chosen = bot_choose_move_medium(tabuleiro, pos[1])
                    else:
                        chosen = bot_choose_move_hard(tabuleiro, pos[1], pos[0], last_player_move)
                    if chosen:
                        nr, nc = chosen
                        tabuleiro[nr][nc] = 1
                        pos[1] = (nr, nc)
                        turno = 0
                    bot_timer = None

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if gear_rect and gear_rect.collidepoint(mx, my):
                    paused = True

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                if not paused:
                    if not vs_bot or turno == 0:
                        if ev.key in keys[turno]:
                            direcao = keys[turno][ev.key]
                            nova = obter_proxima_pos(pos[turno], direcao)
                            if jogada_valida(tabuleiro, nova):
                                tabuleiro[pos[turno][0]][pos[turno][1]] = turno
                                if turno == 0:
                                    last_player_move = (nova[0] - pos[0][0], nova[1] - pos[0][1])
                                pos[turno] = nova
                                tabuleiro[nova[0]][nova[1]] = turno
                                turno = 1 - turno
                                bot_timer = None

        while paused:
            rects, panel_rect = desenhar_pausa_and_get_rects_dynamic(["Retomar Game", "Finalizar Game"])
            pygame.display.flip()
            for pe in pygame.event.get():
                if pe.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if pe.type == pygame.MOUSEBUTTONDOWN and pe.button == 1:
                    mx, my = pe.pos
                    if rects[0].collidepoint(mx, my):
                        paused = False
                        bot_timer = pygame.time.get_ticks() if (vs_bot and turno == 1) else None
                    elif rects[1].collidepoint(mx, my):
                        return None
                if pe.type == pygame.KEYDOWN and pe.key == pygame.K_ESCAPE:
                    paused = False
                    bot_timer = pygame.time.get_ticks() if (vs_bot and turno == 1) else None
            CLOCK.tick(FPS)

        has_move = False
        for dr, dc in KEY_LIST:
            nr, nc = pos[turno][0] + dr, pos[turno][1] + dc
            if jogada_valida(tabuleiro, (nr, nc)):
                has_move = True
                break
        if not has_move:
            winner = 1 - turno
            return winner

        CLOCK.tick(FPS)

# ---- Main ----
def main():
    while True:
        choice = menu_inicial()
        if choice is None:
            pygame.quit(); sys.exit()
        if choice == "RULES":
            mostrar_regras_page()
            continue

        vs_bot, bot_level = choice
        score = [0, 0]

        while max(score) < 3:
            resultado = jogar_round(vs_bot, score, bot_level)
            if resultado is None:
                break
            score[resultado] += 1

            wait_responsive(1000)

            msg = f"P1: {score[0]} - P2: {score[1]}" if not vs_bot else f"You: {score[0]} - Bot: {score[1]}"
            animar_mensagem(msg, BLUE if resultado == 0 else RED, duration_s=0.9)

            wait_responsive(1000)

        if max(score) >= 3:
            if vs_bot:
                final_text = "You Win!" if score[0] > score[1] else "You Lose!"
            else:
                final_text = "P1 Wins!" if score[0] > score[1] else "P2 Wins!"
            animar_mensagem(final_text, BLUE if score[0] > score[1] else RED, duration_s=1.2)
            wait_responsive(1000)

if __name__ == "__main__":
    main()
