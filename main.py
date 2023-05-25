import os
from dotenv import load_dotenv
from github import Github

load_dotenv()


gat = os.getenv("GITHUB_ACCESS_TOKEN", None)
assert gat is not None, "Please set GITHUB_ACCESS_TOKEN in .env file"

g = Github(gat)
search_query = "stars:100..10000 language:python"
result = g.search_repositories(query=search_query, sort="stars", order="desc")

# repo pagination
REPOS_PAGE_SIZE = 4
REPOS_PAGE_NUMBER = 1

# pr pagination
PR_PAGE_SIZE = 4
PR_PAGE_NUMBER = 1

start_index = REPOS_PAGE_SIZE * (REPOS_PAGE_NUMBER - 1)
end_index = REPOS_PAGE_SIZE * REPOS_PAGE_NUMBER
for i, repo in enumerate(result[start_index:end_index]):
    index = REPOS_PAGE_SIZE * (REPOS_PAGE_NUMBER - 1) + i + 1
    print(f"Repo #{index} owner: {repo.owner.login}")
    print(f"Repo #{index} name: {repo.name}")
    print(f"Repo #{index} stars: {repo.stargazers_count}")
    print(f"Repo #{index} url: {repo.html_url}")

    # get recent closed pull requests
    pulls = repo.get_pulls(state="closed", sort="created", direction="desc")
    start_index = PR_PAGE_SIZE * (PR_PAGE_NUMBER - 1)
    end_index = PR_PAGE_SIZE * PR_PAGE_NUMBER
    for i, pr in enumerate(pulls[start_index:end_index]):
        index = PR_PAGE_SIZE * (PR_PAGE_NUMBER - 1) + i + 1
        print(f"\tPR #{index} title: {pr.title}")
        print(f"\tPR #{index} created at: {pr.created_at}")
        print(f"\tPR #{index} merged at: {pr.merged_at}")
        print(f"\tPR #{index} url: {pr.html_url}")
        print(f"\tPR #{index} diff url: {pr.diff_url}")
        print("")
