"""Cached sprite loading plus procedural frame generation (no numpy)."""
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pygame

_ASSETS = Path("src/assets/images")

SPRITE_FILES: Dict[str, str] = {
    "player": "pacman.png",
    "blinky": "blinky.png",
    "pinky": "pinky.png",
    "inky": "inky.png",
    "clyde": "clyde.png",
    "frightened": "frightened.png",
}

_cache: Dict[Tuple[str, int], pygame.Surface] = {}
_frames_cache: Dict[int, List[pygame.Surface]] = {}
_white_cache: Dict[Tuple[str, int], pygame.Surface] = {}


def get_sprite(key: str, size: int) -> pygame.Surface:
    """Return the named sprite scaled to a square of `size`, cached."""
    cache_key = (key, size)
    if cache_key not in _cache:
        path = _ASSETS / SPRITE_FILES[key]
        img = pygame.image.load(str(path)).convert_alpha()
        _cache[cache_key] = pygame.transform.scale(img, (size, size))
    return _cache[cache_key]


def try_get_sprite(key: str, size: int) -> Optional[pygame.Surface]:
    """Like get_sprite, but returns None when the asset is unavailable."""
    if key not in SPRITE_FILES:
        return None
    try:
        return get_sprite(key, size)
    except (pygame.error, FileNotFoundError):
        return None


def get_white_sprite(key: str, size: int) -> pygame.Surface:
    """Return a white silhouette of the sprite (keeps alpha), cached."""
    cache_key = (key, size)
    if cache_key not in _white_cache:
        silhouette = get_sprite(key, size).copy()
        silhouette.fill((255, 255, 255, 255),
                        special_flags=pygame.BLEND_RGBA_MAX)
        _white_cache[cache_key] = silhouette
    return _white_cache[cache_key]


def get_white_sprite_opt(key: str, size: int) -> Optional[pygame.Surface]:
    """Like get_white_sprite, but returns None when unavailable."""
    if key not in SPRITE_FILES:
        return None
    try:
        return get_white_sprite(key, size)
    except (pygame.error, FileNotFoundError):
        return None


def try_get_pacman_frames(size: int) -> Optional[List[pygame.Surface]]:
    """Like get_pacman_frames, but returns None when unavailable."""
    try:
        return get_pacman_frames(size)
    except (pygame.error, FileNotFoundError):
        return None


def get_pacman_frames(size: int) -> List[pygame.Surface]:
    """Return chomp frames [closed, mid, wide] for the player sprite."""
    if size in _frames_cache:
        return _frames_cache[size]

    base = get_sprite("player", size)
    closed = base.copy()
    wide = base.copy()
    w, h = base.get_size()
    cx, cy = w / 2, h / 2
    radius = min(w, h) / 2

    rs = gs = bs = count = 0
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            color = base.get_at((x, y))
            if color.a > 128:
                rs += color.r
                gs += color.g
                bs += color.b
                count += 1
    if count == 0:
        body_color = (255, 255, 0, 255)
    else:
        body_color = (rs // count, gs // count, bs // count, 255)

    transparent = (0, 0, 0, 0)
    for y in range(h):
        for x in range(w):
            dist = math.hypot(x - cx, y - cy)
            if dist > radius * 0.99:
                continue
            angle = abs(math.degrees(math.atan2(-(y - cy), x - cx)))
            alpha = base.get_at((x, y)).a
            if angle <= 30 and alpha <= 128:
                closed.set_at((x, y), body_color)
            elif angle <= 45 and alpha > 128 and dist > radius * 0.12:
                wide.set_at((x, y), transparent)

    _frames_cache[size] = [closed, base, wide]
    return _frames_cache[size]
