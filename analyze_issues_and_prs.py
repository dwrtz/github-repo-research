import json
import csv


def from_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


part1 = from_json("search_info_1k_to_10k_any.json")
part2 = from_json("search_info_10k_to_100k_any.json")
stats = {**part1["stats"], **part2["stats"]}

# Prepare the data for the CSV
rows = []
for key, stats in stats.items():
    row = [key, stats["forks"], stats["stars"], stats["pull_requests"], stats["issues"]]
    rows.append(row)

# Write the data to a CSV file
with open("issues_and_prs_any.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        ["full_name", "forks", "stars", "pull_requests", "issues"]
    )  # Write the header
    writer.writerows(rows)  # Write the data
