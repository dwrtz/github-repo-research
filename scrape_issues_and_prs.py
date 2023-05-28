import os
import time
import json
from github import Github
from datetime import datetime, timedelta
from dotenv import load_dotenv

RATE_LIMIT = 5000  # per hour
MAX_PAGE_SIZE = 100  # Max GitHub API page size
WAIT_TIME = 3600 / (0.9 * RATE_LIMIT)  # in seconds
DEFAULT_PAGE_SIZE = 30  # Default GitHub API page size

# repo pagination
REPOS_PAGE_SIZE = 1024
REPOS_PAGE_NUMBER = 1


def to_json(stats, filename):
    with open(filename, "w") as f:
        json.dump(stats, f)


def get_recent_items(repo, item_type):
    time.sleep(WAIT_TIME)  # Wait to not exceed rate limit
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    item_count = 0
    processed_items = 0  # Add a counter for processed items

    items = item_type(state="all", sort="created", direction="desc")
    for item in items:
        if item.created_at < thirty_days_ago:
            break
        item_count += 1
        processed_items += 1  # Increment the counter

        if processed_items == DEFAULT_PAGE_SIZE:
            time.sleep(WAIT_TIME)  # Wait to not exceed rate limit
            processed_items = 0  # Reset the counter

    return item_count


def analyze_repositories(repos):
    repo_info = {}

    for i, repo in enumerate(repos):
        print(f"Processing Repo #{i+1} : {repo.full_name}")

        pr_count = get_recent_items(repo, repo.get_pulls)
        issue_count = get_recent_items(repo, repo.get_issues)
        forks_count = repo.forks_count
        stars_count = repo.stargazers_count

        print(f"\tPRs: {pr_count} in last 30 days")
        print(f"\tIssues: {issue_count} in last 30 days")
        print(f"\tForks: {forks_count}")
        print(f"\tStars: {stars_count}")

        # Save the information in the dictionary
        repo_info[repo.full_name] = {
            "pull_requests": pr_count,
            "issues": issue_count,
            "forks": forks_count,
            "stars": stars_count,
        }

        time.sleep(WAIT_TIME)  # Wait time to not exceed rate limit

    return repo_info


if __name__ == "__main__":
    load_dotenv()

    gat = os.getenv("GITHUB_ACCESS_TOKEN", None)
    assert gat is not None, "Please set GITHUB_ACCESS_TOKEN in .env file"

    g = Github(gat)
    fstart = 1000
    fend = 5395
    search_query = f"forks:{fstart}..{fend}"
    result = g.search_repositories(query=search_query, sort="forks", order="desc")

    start_index = REPOS_PAGE_SIZE * (REPOS_PAGE_NUMBER - 1)
    end_index = REPOS_PAGE_SIZE * REPOS_PAGE_NUMBER

    repo_stats = analyze_repositories(result[start_index:end_index])
    print(repo_stats)

    search_info = {
        "query": search_query,
        "stats": repo_stats,
    }

    to_json(search_info, f"search_info_{fstart//1000}k_to_{fend//1000}k_any.json")
