import os
import requests
import subprocess


def get_open_pull_requests(base_repo_owner, base_repo_name, github_token):
    url = f"https://api.github.com/repos/{base_repo_owner}/{base_repo_name}/pulls"
    headers = {"Authorization": f"Bearer {github_token}", "Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_pull_request(base_repo_owner, base_repo_name, fork_repo_owner, fork_repo_name, pr_data, github_token):
    base_branch = pr_data["base"]["ref"]
    fork_branch = f'{base_branch}_replica'
    # Define API endpoints
    base_url = f"https://api.github.com/repos/{base_repo_owner}/{base_repo_name}"
    fork_url = f"https://api.github.com/repos/{fork_repo_owner}/{fork_repo_name}"

    # Create a new branch in the forked repository
    create_branch_url = f"{fork_url}/git/refs"
    create_branch_payload = {
        "ref": f"refs/heads/{fork_branch}",
        "sha": get_branch_sha(base_repo_owner, base_repo_name, base_branch, github_token)
    }
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.post(create_branch_url, json=create_branch_payload, headers=headers)
    if response.status_code != 201:
        print("Failed to create branch in the forked repository.")
        return

    # Cherry-pick all commits from the base branch
    cherry_pick_url = f"{fork_url}/git/commits"
    cherry_pick_payload = {
        "parents": [get_branch_sha(fork_repo_owner, fork_repo_name, fork_branch, github_token)],
        "tree": get_branch_sha(base_repo_owner, base_repo_name, base_branch, github_token)
    }
    response = requests.post(cherry_pick_url, json=cherry_pick_payload, headers=headers)
    if response.status_code != 201:
        print("Failed to cherry-pick commits.")
        return
    new_commit_sha = response.json()["sha"]

    # Update the new branch reference
    update_branch_url = f"{fork_url}/git/refs/heads/{fork_branch}"
    update_branch_payload = {
        "sha": new_commit_sha
    }
    response = requests.patch(update_branch_url, json=update_branch_payload, headers=headers)
    if response.status_code != 200:
        print("Failed to update branch reference.")
        return

    # Create pull request
    create_pr_url = f"{base_url}/pulls"
    create_pr_payload = {
        "title": "Pull Request Title",
        "body": "Pull Request Body",
        "head": f"{fork_repo_owner}:{fork_branch}",
        "base": base_branch
    }
    response = requests.post(create_pr_url, json=create_pr_payload, headers=headers)
    if response.status_code != 201:
        print("Failed to create pull request.")
        return

    print("Pull request created successfully.")

def get_branch_sha(repo_owner, repo_name, branch, github_token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs/heads/{branch}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["object"]["sha"]
    else:
        print(f"Failed to fetch SHA for branch {branch}.")
        return None
    
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
        create_pull_request(base_repo_owner, base_repo_name, fork_repo_owner, fork_repo_name, pr, github_token)

if __name__ == "__main__":
    main()
