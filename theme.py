"""
Theme constants for Aviator Oracle.
Dark cockpit aesthetic with amber/teal accents.
"""

# Background colors
BG_DARK    = (0.07, 0.07, 0.10, 1)
BG_CARD    = (0.11, 0.11, 0.16, 1)
BG_INPUT   = (0.14, 0.14, 0.20, 1)

# Accent colors
ACCENT_AMBER = (0.93, 0.63, 0.15, 1)   # amber
ACCENT_TEAL  = (0.11, 0.62, 0.46, 1)   # teal/green
ACCENT_RED   = (0.89, 0.29, 0.29, 1)   # crash red
ACCENT_BLUE  = (0.22, 0.54, 0.87, 1)   # info blue

# Text colors
TEXT_PRIMARY   = (0.95, 0.95, 0.95, 1)
TEXT_SECONDARY = (0.60, 0.60, 0.70, 1)
TEXT_TERTIARY  = (0.40, 0.40, 0.50, 1)
TEXT_DARK      = (0.07, 0.07, 0.10, 1)

# Multiplier color coding
def mult_color(v):
    if v < 1.5:
        return ACCENT_RED
    elif v < 3.0:
        return ACCENT_AMBER
    else:
        return ACCENT_TEAL

# Tab labels
TABS = ['PREDICT', 'HISTORY', 'STATS', 'BANKROLL']
