import os
from dotenv import load_dotenv
from github import Github

load_dotenv()


gat = os.getenv("GITHUB_ACCESS_TOKEN", None)
assert gat is not None, "Please set GITHUB_ACCESS_TOKEN in .env file"

g = Github(gat)
search_query = "stars:>=1000 language:python"
result = g.search_repositories(query=search_query, sort="stars", order="desc")

PAGE_SIZE = 4
PAGE_NUMBER = 1

for i, repo in enumerate(
    result[PAGE_SIZE * (PAGE_NUMBER - 1) : PAGE_SIZE * PAGE_NUMBER]
):
    index = PAGE_SIZE * (PAGE_NUMBER - 1) + i + 1
    print(f"Repo #{index} owner: {repo.owner.login}")
    print(f"Repo #{index} name: {repo.name}")
    print(f"Repo #{index} stars: {repo.stargazers_count}")
    print(f"Repo #{index} url: {repo.html_url}")
    print("")
