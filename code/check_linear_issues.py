#!/usr/bin/env python3
"""
Check open Linear issues with Windows-safe output
"""
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from devenviro.terminal_output import print_success, print_error, print_info, safe_print


def get_open_linear_issues():
    """Fetch and display open Linear issues"""
    
    # Load environment
    project_root = Path.cwd()
    env_file = project_root / 'config' / 'secrets' / '.env'
    load_dotenv(env_file)

    api_key = os.getenv('LINEAR_API_KEY')
    if not api_key or api_key == 'YOUR_ACTUAL_KEY_HERE':
        print_error('Linear API key not configured')
        return False

    # Query for open issues
    query = '''
    {
      issues(filter: { state: { type: { nin: ["completed", "canceled"] } } }) {
        nodes {
          id
          title
          state { name }
          priority
          assignee { name email }
          createdAt
          updatedAt
          url
        }
      }
    }
    '''

    try:
        safe_print("[API] Connecting to Linear...")
        response = requests.post(
            'https://api.linear.app/graphql',
            json={'query': query},
            headers={'Authorization': api_key},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            issues = data.get('data', {}).get('issues', {}).get('nodes', [])
            
            if issues:
                print_info(f"Found {len(issues)} open Linear issues:")
                print()
                
                for issue in issues:
                    assignee = issue.get('assignee')
                    assignee_name = assignee['name'] if assignee else 'Unassigned'
                    
                    # Clean title of unicode characters
                    title = issue['title']
                    # Replace common unicode characters that might appear in titles
                    title = title.encode('ascii', 'replace').decode('ascii')
                    
                    safe_print(f"  • {title}")
                    safe_print(f"    State: {issue['state']['name']} | Priority: {issue.get('priority', 'None')} | Assignee: {assignee_name}")
                    safe_print(f"    URL: {issue['url']}")
                    print()
                    
                return True
            else:
                print_success('No open Linear issues found')
                return True
        else:
            print_error(f'API request failed: {response.status_code}')
            safe_print(response.text)
            return False
            
    except Exception as e:
        print_error(f'Failed to fetch Linear issues: {e}')
        return False


if __name__ == "__main__":
    get_open_linear_issues()