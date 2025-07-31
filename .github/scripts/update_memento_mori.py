import datetime

# === CONFIGURATION ===
birth_date = datetime.date(1990, 11, 18)
life_expectancy_years = 90
char_lived = "."
char_skipped = "S"

today = datetime.date.today()
start_year = birth_date.year
weeks_per_year = 52

grid = ""

for year_index in range(life_expectancy_years):
    year = start_year + year_index
    line = f"{year} ({year_index + 1:2d})  "

    jan_1 = datetime.date(year, 1, 1)
    dec_31 = datetime.date(year, 12, 31)

    # Generate week start dates for the year
    week_starts = []
    week_start = jan_1
    while week_start <= dec_31:
        week_starts.append(week_start)
        week_start += datetime.timedelta(weeks=1)

    # Pad to 52 weeks if needed
    while len(week_starts) < weeks_per_year:
        week_starts.append(dec_31)

    for ws in week_starts:
        if ws < birth_date:
            line += char_skipped  # Not born yet = skipped
        elif ws <= today:
            line += char_lived    # Lived week = dot
        else:
            line += char_skipped  # Future weeks = skipped

    grid += line + "\n"

# Calculate summary stats
total_weeks = life_expectancy_years * weeks_per_year
weeks_lived = sum(1 for line in grid.splitlines() for c in line[10:] if c == char_lived)
weeks_skipped = total_weeks - weeks_lived

summary = (
    "\nOK, but incomplete, skipped, or risky tests!\n"
    f"Tests: {total_weeks}, Assertions: {total_weeks}, Skipped: {weeks_skipped}.\n"
)

# Wrap the entire block in triple backticks for markdown formatting
full_output = "```\n" + grid + summary + "```\n"

# === UPDATE README.md ===
with open("README.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

start_marker = "<!-- MM_START -->"
end_marker = "<!-- MM_END -->"
new_lines = []
inside = False

for line in lines:
    if start_marker in line:
        new_lines.append(start_marker + "\n")
        new_lines.append(full_output)
        inside = True
    elif end_marker in line:
        new_lines.append(end_marker + "\n")
        inside = False
    elif not inside:
        new_lines.append(line)

with open("README.md", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
