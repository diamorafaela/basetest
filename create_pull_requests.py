import os
import requests


def get_open_pull_requests(base_repo_owner, base_repo_name, github_token):
    url = f"https://api.github.com/repos/{base_repo_owner}/{base_repo_name}/pulls"
    headers = {"Authorization": f"Bearer {github_token}", "Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_pull_request(base_repo_owner, base_repo_name, fork_repo_owner, fork_repo_name, pr_data, github_token):
def create_pull_request(base_repo_owner, base_repo_name, fork_repo_owner, fork_repo_name, pr_number, github_token):
    # Fetch pull request details from the base repository
    pr_url = pr_data['url']
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(pr_url, headers=headers)
    response.raise_for_status()
    pr_data = response.json()
    
    # Extract source branch information from the pull request
    source_branch = pr_data["head"]["ref"]
    commit_sha = pr_data["head"]["sha"]

    # Create a new branch in the forked repository with the same changes
    new_branch_name = f"pr_{pr_number}_from_{source_branch}"
    new_branch_url = f"https://api.github.com/repos/{fork_repo_owner}/{fork_repo_name}/git/refs"
    data = {
        "ref": f"refs/heads/{new_branch_name}",
        "sha": commit_sha
    }
    response = requests.post(new_branch_url, json=data, headers=headers)
    response.raise_for_status()

    # Create the pull request in the forked repository
    pr_data = {
        "title": pr_data["title"],
        "body": pr_data["body"],
        "head": new_branch_name,
        "base": pr_data["base"]["ref"]
    }
    pr_url = f"https://api.github.com/repos/{fork_repo_owner}/{fork_repo_name}/pulls"
    response = requests.post(pr_url, json=pr_data, headers=headers)
    response.raise_for_status()
    
    return response.json()

def main():
    base_repo_owner = os.getenv("BASE_REPO_OWNER")
    base_repo_name = os.getenv("BASE_REPO_NAME")
    fork_repo_owner = os.getenv("FORK_REPO_OWNER")
    fork_repo_name = os.getenv("FORK_REPO_NAME")
    github_token = os.getenv("GITHUB_TOKEN")

    open_pull_requests = get_open_pull_requests(base_repo_owner, base_repo_name, github_token)

    for pr in open_pull_requests:
        # Check if the pull request has already been processed
        # You may implement this check based on your specific requirements

        # Create a corresponding pull request in the forked repository
        created_pr = create_pull_request(base_repo_owner, base_repo_name, fork_repo_owner, fork_repo_name, pr, github_token)
        print(f"Created pull request: {created_pr['html_url']}")

if __name__ == "__main__":
    main()
