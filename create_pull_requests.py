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
    # Clone the branch from the base repository
    base_branch = pr_data["head"]["ref"]
    clone_url = f"https://github.com/{base_repo_owner}/{base_repo_name}.git"
    clone_dir = f"/tmp/{base_repo_name}_{base_branch}"
    clone_command = f"git clone --single-branch --branch {base_branch} {clone_url} {clone_dir}"
    subprocess.run(clone_command, shell=True, check=True)

    # Create a new branch in the forked repository with the same content
    fork_branch = f"{pr_data['base']['ref']}_from_{base_branch}"
    subprocess.run(f"cd {clone_dir} && git checkout -b {fork_branch} && git push origin {fork_branch}", shell=True, check=True)

    # Create the pull request
    url = f"https://api.github.com/repos/{fork_repo_owner}/{fork_repo_name}/pulls"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": pr_data["title"],
        "body": pr_data["body"],
        "head": fork_branch,  # Use the newly created branch in the forked repository
        "base": pr_data["base"]["ref"]
    }
    response = requests.post(url, json=data, headers=headers)
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
