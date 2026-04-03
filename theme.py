"""ثيم AliJaddi — ألوان فاتح/مظلم + زخارف هندسية + RTL عربي."""
from __future__ import annotations
import flet as ft

# ─── Light palette ───
L_BG        = "#F5F7FA"
L_HEADER    = "#FFFFFF"
L_CARD      = "#FFFFFF"
L_TEXT      = "#1E293B"
L_TEXT2     = "#64748B"
L_BORDER    = "#E2E8F0"
L_DOT       = "#E2E8F0"

# ─── Dark palette ───
D_BG        = "#121826"
D_HEADER    = "#1E293B"
D_CARD      = "#1E293B"
D_TEXT      = "#F1F5F9"
D_TEXT2     = "#94A3B8"
D_BORDER    = "#334155"
D_DOT       = "#334155"

# ─── Brand / Accent ───
PRIMARY     = "#3B82F6"
PRIMARY_D   = "#2563EB"
DANGER      = "#EF4444"
DANGER_D    = "#DC2626"
STAR        = "#F59E0B"
STAR_D      = "#FBBF24"
SUCCESS     = "#22C55E"
ACCENT_CYAN = "#06B6D4"

# ─── Model accent colours ───
MODEL_COLORS = {
    "euqid":              "#F97316",
    "tahlil":             "#3B82F6",
    "zakhrafatan":        "#8B5CF6",
    "sniper_perspective": "#EF4444",
    "mudir":              "#06B6D4",
    "legal":              "#3B82F6",
    "maps":               "#22C55E",
    "adich":              "#A855F7",
    "sniper":             "#EF4444",
}


def is_dark(page: ft.Page) -> bool:
    return page.theme_mode == ft.ThemeMode.DARK


def bg(page):       return D_BG     if is_dark(page) else L_BG
def header(page):   return D_HEADER if is_dark(page) else L_HEADER
def card(page):     return D_CARD   if is_dark(page) else L_CARD
def tx(page):       return D_TEXT   if is_dark(page) else L_TEXT
def tx2(page):      return D_TEXT2  if is_dark(page) else L_TEXT2
def border(page):   return D_BORDER if is_dark(page) else L_BORDER
def dot(page):      return D_DOT    if is_dark(page) else L_DOT
def star(page):     return STAR_D   if is_dark(page) else STAR
def primary(page):  return PRIMARY_D if is_dark(page) else PRIMARY


def apply_theme(page: ft.Page, dark: bool = True):
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK if dark else ft.ThemeMode.LIGHT
    page.bgcolor = D_BG if dark else L_BG
    page.theme = ft.Theme(
        color_scheme_seed=PRIMARY,
        visual_density=ft.VisualDensity.COMPACT,
    )
    page.dark_theme = ft.Theme(color_scheme_seed=PRIMARY_D)
