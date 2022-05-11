"""
Github session stuff
"""

import github


def github_login(token: str, repo: str):
    gh = github.Github(login_or_token=token)
    return gh.get_repo(repo)
