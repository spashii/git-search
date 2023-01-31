import argparse
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Print iterations progress
def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def clone_or_pull_repo(repo_url, repo_folder_name):
    if os.path.exists(repo_folder_name):
        print(f"[INFO] Repo {repo_folder_name} already exists. Pulling changes...")
        subprocess.run(["git", "pull"], cwd=repo_folder_name)
    else:
        print(f"[INFO] Repo {repo_folder_name} not found. Cloning...")
        try:
            subprocess.run(["git", "clone", repo_url, repo_folder_name])
        except:
            print(f"[ERROR] Repo {repo_url} not found. Check if repo is public or if you have access to it.")

from concurrent.futures import ThreadPoolExecutor, as_completed

def search_repo(repo_folder_name, search_regex):
    branches = subprocess.run(["git", "branch", "-a", "--format=%(refname:short)"], cwd=repo_folder_name, capture_output=True).stdout.decode().strip().split("\n")
    print(f"[INFO] {len(branches)} branches found.")

    search_results = []
    index = 0

    print(f"[INFO] Using {args.threads} threads.")
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(search_branch, branch, repo_folder_name, search_regex, index): branch for branch in branches}
        completed = 0
        for future in as_completed(futures):
            branch = futures[future]
            branch_results = future.result()
            search_results.extend(branch_results)
            index += len(branch_results)
            completed += 1
            print_progress_bar(completed, len(branches), prefix = '[INFO] Progress:', suffix = 'Complete', length = 50)
    return search_results

def search_branch(branch, repo_folder_name, search_regex, index):
    branch_results = subprocess.run(["git", "grep", "-n", search_regex, branch], cwd=repo_folder_name, capture_output=True).stdout.decode().strip()
    if branch_results:
        results = []
        for result in branch_results.split("\n"):
            result_parts = result.split(":")
            results.append({
                "branch": branch,
                "file_name": result_parts[1],
                "line_number": result_parts[2],
                "line": result_parts[3],
                # "commit_hash": subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_folder_name, capture_output=True).stdout.decode().strip()
            })
            index += 1
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_url", help="URL of the git repository to search.")
    parser.add_argument("search_regex", help="Regex to search for.")
    parser.add_argument("--threads", help="Number of threads to use for parallel processing.", default=4, type=int)
    args = parser.parse_args()

    repo_name = args.repo_url.split("/")[-1].split(".")[0]
    repo_folder_name = f"repos/{repo_name}"
    search_regex = args.search_regex

    print(f"[INFO] Searching for '{search_regex}' in '{repo_name}'...")

    clone_or_pull_repo(args.repo_url, repo_folder_name)
    search_results = search_repo(repo_folder_name, search_regex)

    print(f"[INFO] {len(search_results)} results found.")
    print(json.dumps(search_results, indent=4))

    result_path = f"results/{repo_name}_{int(time.time())}.json"

    if not os.path.exists("results"):
        os.makedirs("results")

    with open(result_path, "w") as f:
        json.dump(search_results, f, indent=4)
    

