# git-search

* The repository is cloned (or) pulled, if exists, to `repos`
* Results are stored in `results`

## Usage

* Authenticate with a [personal access token]([https://gith](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)) if necessary: 
(https://{username}:{personal_access_token}@{repo_url})


```
usage: python main.py [-h] [--threads THREADS] repo_url search_regex

positional arguments:
  repo_url           URL of the git repository to search.
  search_regex       Regex to search for.

optional arguments:
  -h, --help         show this help message and exit
  --threads THREADS  Number of threads to use for parallel processing.
```