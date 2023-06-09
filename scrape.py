import os
import time
from dotenv import load_dotenv
from github import Github
from helpers import (
    Repository,
    TokenCounts,
    PullRequest,
    to_json,
    get_diff,
    count_tokens,
)


RATE_LIMIT = 5000  # per hour
WAIT_TIME = 3600 / (0.9 * RATE_LIMIT)  # in seconds

# repo pagination
REPOS_PAGE_SIZE = 64
REPOS_PAGE_NUMBER = 1

# pr pagination
PR_PAGE_SIZE = 64
PR_PAGE_NUMBER = 1


if __name__ == "__main__":
    load_dotenv()

    gat = os.getenv("GITHUB_ACCESS_TOKEN", None)
    assert gat is not None, "Please set GITHUB_ACCESS_TOKEN in .env file"

    g = Github(gat)
    search_query = "stars:100..10000 language:python"
    result = g.search_repositories(query=search_query, sort="stars", order="desc")

    pull_requests = []

    start_index = REPOS_PAGE_SIZE * (REPOS_PAGE_NUMBER - 1)
    end_index = REPOS_PAGE_SIZE * REPOS_PAGE_NUMBER
    for i, repo in enumerate(result[start_index:end_index]):
        time.sleep(WAIT_TIME)
        index = REPOS_PAGE_SIZE * (REPOS_PAGE_NUMBER - 1) + i + 1
        repository = Repository(
            owner=repo.owner.login,
            name=repo.name,
            stars=repo.stargazers_count,
            url=repo.html_url,
        )

        print(f"Repo #{index} owner: {repository.owner}")
        print(f"Repo #{index} name: {repository.name}")
        print(f"Repo #{index} stars: {repository.stars}")
        print(f"Repo #{index} url: {repository.url}")

        # get recent closed pull requests
        pulls = repo.get_pulls(state="closed", sort="created", direction="desc")
        start_index = PR_PAGE_SIZE * (PR_PAGE_NUMBER - 1)
        end_index = PR_PAGE_SIZE * PR_PAGE_NUMBER
        for i, pr in enumerate(pulls[start_index:end_index]):
            time.sleep(WAIT_TIME)
            index = PR_PAGE_SIZE * (PR_PAGE_NUMBER - 1) + i + 1
            diff = get_diff(pr.diff_url)
            token_counts = TokenCounts(
                title=count_tokens(pr.title),
                body=count_tokens(pr.body),
                diff=count_tokens(diff),
            )
            pull_request = PullRequest(
                title=pr.title,
                body=pr.body,
                created_at=pr.created_at,
                merged_at=pr.merged_at,
                url=pr.html_url,
                diff_url=pr.diff_url,
                diff=diff,
                repository=repository,
                token_counts=token_counts,
            )
            pull_requests.append(pull_request)

            print(f"\tPR #{index} title: {pull_request.title}")
            print(f"\tPR #{index} created at: {pull_request.created_at}")
            print(f"\tPR #{index} merged at: {pull_request.merged_at}")
            print(f"\tPR #{index} url: {pull_request.url}")
            print(f"\tPR #{index} diff url: {pull_request.diff_url}")
            print(f"\tPR #{index} diff token count: {token_counts.diff}")
            print("")

# save to json
to_json(pull_requests, "data.json")
