import os
import time
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

RATE_LIMIT = 1800  # per hour
MAX_PAGE_SIZE = 100  # Max GitHub API page size
WAIT_TIME = 3600 / (0.9 * RATE_LIMIT)  # in seconds


def to_json(stats, filename):
    with open(filename, "w") as f:
        json.dump(stats, f)


def fetch_count(url_template, headers, full_name, thirty_days_ago):
    time.sleep(WAIT_TIME)  # Respect rate limit
    # Make a request for the first page
    response = requests.get(
        url_template.format(
            full_name,
            thirty_days_ago,
            datetime.now().isoformat(),
            30,  # Page size (default)
            1,  # Page number
        ),
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception(f"Request failed with status {response.status_code}")

    # Return the total count
    return response.json()["total_count"]


if __name__ == "__main__":
    load_dotenv()

    gat = os.getenv("GITHUB_ACCESS_TOKEN", None)
    assert gat is not None, "Please set GITHUB_ACCESS_TOKEN in .env file"

    headers = {"Authorization": f"Bearer {gat}"}

    # Maximum repositories we can fetch due to GitHub's API pagination limit
    max_repos = 10000
    page_size = MAX_PAGE_SIZE
    pages = max_repos // page_size
    star_threshold = 1000

    # URL for the GitHub Search API
    url_template = "https://api.github.com/search/repositories?q=stars:%3E{}&sort=updated&order=desc&per_page={}&page={}"

    # URL templates for the issue and pull request searches
    pr_url_template = "https://api.github.com/search/issues?q=repo:{}+is:pr+created:{}..{}&per_page={}&page={}"
    issue_url_template = "https://api.github.com/search/issues?q=repo:{}+is:issue+created:{}..{}&per_page={}&page={}"

    # Calculate date 30 days ago
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

    # Initialize the dict for storing repository info
    repo_info = {}

    # Fetch the most recently updated repos
    for page in range(1, pages + 1):
        time.sleep(WAIT_TIME)  # Respect rate limit
        response = requests.get(
            url_template.format(star_threshold, page_size, page), headers=headers
        )
        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}")
        repos = response.json()["items"]
        for i, repo in enumerate(repos):
            index = page_size * (page - 1) + i + 1
            full_name = repo["full_name"]
            print(f"Processing Repo #{index}: {full_name}")
            pr_count = fetch_count(pr_url_template, headers, full_name, thirty_days_ago)
            print(f"\tPRs: {pr_count} in last 30 days")
            issue_count = fetch_count(
                issue_url_template, headers, full_name, thirty_days_ago
            )
            print(f"\tIssues: {issue_count} in last 30 days")

            # Store the info in the dict
            repo_info[repo["full_name"]] = {
                "updated_at": repo["updated_at"],
                "pr_count": pr_count,
                "issue_count": issue_count,
            }

        # save after each page
        to_json(repo_info, "recently_updated.json")

    print(repo_info)
