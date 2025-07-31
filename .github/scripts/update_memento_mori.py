import datetime
from dateutil.relativedelta import relativedelta

# === CONFIGURATION ===
birth_date = datetime.date(1990, 11, 18)
life_expectancy_years = 90
char_lived = "."
char_skipped = "-"
weeks_per_year = 52

today = datetime.date.today()
start_year = birth_date.year

output = []
output.append("Pest v2.8.14 by Nuno Maduro\n\n")

total_tests = life_expectancy_years * weeks_per_year
total_lived = 0
total_skipped = 0

for year_index in range(life_expectancy_years):
    year = start_year + year_index

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

    line_progress = ""
    lived_weeks = 0

    for ws in week_starts:
        if ws < birth_date:
            line_progress += char_skipped
        elif ws <= today:
            line_progress += char_lived
            lived_weeks += 1
        else:
            line_progress += char_skipped

    percent = int((lived_weeks / weeks_per_year) * 100)
    # Format line with suite name, progress bar and progress stats
    line = f"{year} ({year_index:02d})  {line_progress}  {lived_weeks:02d} / {weeks_per_year} ({percent:3d}%)"
    output.append(line + "\n")

    total_lived += lived_weeks
    total_skipped += (weeks_per_year - lived_weeks)

# Calculate lived time difference as years, months, days
diff = relativedelta(today, birth_date)

def format_ymd(diff):
    parts = []
    if diff.years > 0:
        parts.append(f"{diff.years} year{'s' if diff.years != 1 else ''}")
    if diff.months > 0:
        parts.append(f"{diff.months} month{'s' if diff.months != 1 else ''}")
    if diff.days > 0:
        parts.append(f"{diff.days} day{'s' if diff.days != 1 else ''}")
    return ", ".join(parts)

time_lived_str = format_ymd(diff)

summary = (
    f"\nTests: {total_tests}\n"
    f"Passes: {total_lived}\n"
    f"Skips: {total_skipped}\n"
    f"Time: {time_lived_str}\n"
    f"Memory: 0.10 MB\n"
)

output.append(summary)

# Wrap all output in triple backticks for markdown
final_output = "```\n" + "".join(output) + "```\n"

# === UPDATE README.md ===
start_marker = "<!-- MM_START -->"
end_marker = "<!-- MM_END -->"

with open("README.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
inside = False

for line in lines:
    if start_marker in line:
        new_lines.append(start_marker + "\n")
        new_lines.append(final_output)
        inside = True
    elif end_marker in line:
        new_lines.append(end_marker + "\n")
        inside = False
    elif not inside:
        new_lines.append(line)

with open("README.md", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
