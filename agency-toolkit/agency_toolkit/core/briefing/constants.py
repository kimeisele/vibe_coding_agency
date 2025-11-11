"""Constants for PDF briefing generation.

All PDF styling magic numbers extracted here for maintainability.
"""

# Font sizes
FONT_SIZE_TITLE = 24
FONT_SIZE_SECTION_HEADER = 14
FONT_SIZE_TIMESTAMP = 10
FONT_SIZE_BODY = 11

# Line heights (cell height in mm)
LINE_HEIGHT_TITLE = 10
LINE_HEIGHT_SECTION_HEADER = 10
LINE_HEIGHT_BODY = 8
LINE_HEIGHT_MULTI_CELL = 6

# Spacing (ln() values in mm)
SPACING_AFTER_HEADER = 5
SPACING_AFTER_SECTION = 5
SPACING_BETWEEN_ITEMS = 2
SPACING_AFTER_DELIVERABLES = 3

# Font faces
FONT_FAMILY = "Helvetica"
FONT_STYLE_BOLD = "B"
FONT_STYLE_NORMAL = ""

# Template constants
DEFAULT_BUDGET_PRECISION = 2  # Decimal places for currency

# Max cost threshold for logging (in USD)
MAX_COST_WARNING_THRESHOLD = 5000.0
