#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

def check_commit_message():
    print("Trying to build and commit its output...")
    # Get commit message
    with open(sys.argv[1], mode="r", encoding='utf-8') as file:
        commit_message = file.read().strip()

    # Get project root directory path
    # Current directory is ${PROJECT_ROOT}/.git/hooks
    rootdir = Path(__file__).parent.parent 

    # Build
    if not subprocess.run('hugo').returncode == 0:
        print('Hugo build failed')
        sys.exit(1)

    # Commit build output
    if not subprocess.run(
        ['git', 'commit', '-m', commit_message],
        cwd=rootdir / 'public',
        check=True
    ).returncode == 0:
        print("Commit build output failed")
        sys.exit(1)

    print('Success!')

if __name__ == "__main__":
    check_commit_message()
