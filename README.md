# Codacy Security Enabler

This Python script automates the process of enabling and configuring security tools (Trivy and Semgrep) for multiple repositories in Codacy.

## Prerequisites

- Python 3.x
- `requests` library (install using `pip install requests`)
- Codacy API token
- List of repositories in a `repos.txt` file

## Setup

1. Clone this repository or download the `main.py` script.
2. Install the required library:
   ```
   pip install -r requirements.txt
   ```
3. Create a `repos.txt` file in the same directory as the `main.py` script.
4. Add the names of the repositories you want to configure, one per line, in the `repos.txt` file. For example:
   ```
   repo1
   repo2
   repo3
   ```

## Usage

Run the script from the command line with the following parameters:

    ```
    python main.py --provider <provider> --organization <organization> --token <your_codacy_api_token>
    ```

Replace `<provider>`, `<organization>`, and `<your_codacy_api_token>` with your actual Codacy provider, organization, and API token.

Notes:

- The script assumes that the repositories are already added to Codacy. If a repository is not found, the script will skip it.
