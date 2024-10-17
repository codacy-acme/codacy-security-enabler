#!/usr/bin/env python3
import argparse
import requests
import json
import os
import time


TRIVY_TOOL_UUID = "2fd7fbe0-33f9-4ab3-ab73-e9b62404e2cb"
SEMGREP_TOOL_UUID = "6792c561-236d-41b7-ba5e-9d6bee0d548b"




def fetch_tool_patterns(tool_uuid, api_key, limit=100):
    base_url = f"https://app.codacy.com/api/v3/tools/{tool_uuid}/patterns"
    headers = {
        'Accept': 'application/json',
        'api-token': api_key
    }
    params = {'limit': limit}
    all_patterns = []

    while True:
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching patterns: {response.status_code}")
            return None

        data = response.json()
        all_patterns.extend(data['data'])

        if 'pagination' in data and 'cursor' in data['pagination'] and data['pagination']['cursor']:
            params['cursor'] = data['pagination']['cursor']
        else:
            break

    return all_patterns



def configure_codacy_tool(provider, organization, repo_name, tool_uuid, api_key, patterns):
    url = f"https://app.codacy.com/api/v3/analysis/organizations/{provider}/{organization}/repositories/{repo_name}/tools/{tool_uuid}"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'api-token': api_key
    }
    
    body = {
        "enabled": True,
        "useConfigurationFile": False,
        "patterns": patterns
    }
    
    response = requests.patch(url, headers=headers, json=body)
    
    if response.status_code == 204:
        print("Tool configured successfully")
        return
    else:
        print(f"Error configuring tool: {response.status_code}")
        return None


def main():
    print("Welcome to Codacy Security Enabler")
    parser = argparse.ArgumentParser(description='Codacy Engine Helper')
    parser.add_argument('--api-token', dest='token', default=None,
                        help='the api-token to be used on the REST API')
    parser.add_argument('--provider', dest='provider',
                        default=None, help='git provider (gh,gl,bb)')
    parser.add_argument('--organization', dest='organization',
                        default=None, help='organization name')
    
    args = parser.parse_args()

    # Validate input arguments
    if not args.token:
        print("Error: API token is required. Please provide --api-token.")
        return

    if not args.provider:
        print("Error: Provider is required. Please provide --provider (gh, gl, or bb).")
        return

    if not args.organization:
        print("Error: Organization name is required. Please provide --organization.")
        return

    # Validate provider input
    valid_providers = ['gh', 'gl', 'bb']
    if args.provider not in valid_providers:
        print(f"Error: Invalid provider. Please choose from {', '.join(valid_providers)}.")
        return

    print("Input arguments validated successfully.")

    # Validate the existence of repos.txt file
    if not os.path.isfile('repos.txt'):
        print("Error: repos.txt file not found.")
        print("Please create a repos.txt file in the same directory as this script.")
        print("Add one repository name per line in the file.")
        print("Example content of repos.txt:")
        print("repo1")
        print("repo2")
        print("repo3")
        return

    # Check if repos.txt is empty
    if os.stat('repos.txt').st_size == 0:
        print("Error: repos.txt file is empty.")
        print("Please add at least one repository name to the file.")
        return

    print("repos.txt file found and is not empty.")

    security_tools = [TRIVY_TOOL_UUID,
                      SEMGREP_TOOL_UUID
                      ]

    for tool in security_tools:
        print(f"Enabling {tool} for {args.provider} {args.organization}")
        patterns = fetch_tool_patterns(tool, args.token)
        mapped_patterns = []
        for pattern in patterns:
            if not pattern["enabled"]:
                continue
            mapped_pattern = {
                "id": pattern["id"],
                "enabled": pattern["enabled"]
            }
            
            if "parameters" in pattern:
                mapped_parameters = []
                for param in pattern["parameters"]:
                    mapped_param = {
                        "name": param["name"],
                        "value": param.get("default", "")
                    }
                    mapped_parameters.append(mapped_param)
                
                if mapped_parameters:
                    mapped_pattern["parameters"] = mapped_parameters
            
            mapped_patterns.append(mapped_pattern)
        
        patterns = mapped_patterns
        # Read repo names from repos.txt
        with open('repos.txt', 'r') as file:
            repos = [line.strip() for line in file if line.strip()]
        
        # Configure Codacy tool for each repo
        for repo in repos:
            print(f"Configuring {tool} for repo: {repo}")
            configure_codacy_tool(args.provider, args.organization, repo, tool, args.token, patterns)
            # Sleep for 1 second to avoid rate limit
            time.sleep(1)

if __name__ == "__main__":
    main()
