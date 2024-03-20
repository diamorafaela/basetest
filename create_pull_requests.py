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
    # Clone the forked repository
    subprocess.run(['git', 'clone', f'https://github.com/{fork_repo_owner}/{fork_repo_name}.git'])

    # Change directory to the cloned repository
    subprocess.run(['cd', fork_repo_name])

    # Add base repository as remote
    subprocess.run(['git', 'remote', 'add', 'base', f'https://github.com/{base_repo_owner}/{base_repo_name}.git'])

    # Fetch changes from the base repository
    subprocess.run(['git', 'fetch', 'base'])

    # Create a new branch in the forked repository
    subprocess.run(['git', 'checkout', '-b', fork_branch])

    # Cherry-pick all commits from the base branch
    subprocess.run(['git', 'cherry-pick', f'base/{base_branch}'])

    # Push changes to the forked repository
    subprocess.run(['git', 'push', 'origin', fork_branch])

    # Create pull request in the forked repository
    # subprocess.run(['gh', 'pr', 'create', '--base', base_branch, '--head', fork_branch, '--title', 'Pull Request Title', '--body', 'Pull Request Body'])
    # Create pull request using GitHub API
    pull_request_data = {
        "title": "Pull Request Title",
        "body": "Pull Request Body",
        "head": f"{fork_repo_owner}:{fork_branch}",
        "base": base_branch
    }

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    create_pr_url = f"https://api.github.com/repos/{base_repo_owner}/{base_repo_name}/pulls"

    response = requests.post(create_pr_url, json=pull_request_data, headers=headers)

    if response.status_code == 201:
        print("Pull request created successfully.")
    else:
        print("Failed to create pull request.")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")

    # Cleanup cloned repository
    subprocess.run(['cd', '..'])
    subprocess.run(['rm', '-rf', fork_repo_name])


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
