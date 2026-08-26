import requests
import json
import sys

BASE_URL = "http://localhost:8001/api/v1"

def main():
    print("Getting dev token...")
    resp = requests.get(f"{BASE_URL}/auth/dev-token")
    if not resp.ok:
        print("Failed to get dev token", resp.text)
        sys.exit(1)
        
    token = resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Getting workspaces...")
    resp = requests.get(f"{BASE_URL}/workspaces/", headers=headers)
    workspaces_data = resp.json()
    
    workspaces = workspaces_data.get("data", workspaces_data) if isinstance(workspaces_data, dict) else workspaces_data
    if not workspaces:
        print("No workspaces found. Cannot test.")
        sys.exit(1)
    workspace_id = workspaces[0]["id"]
    
    print("Getting projects...")
    resp = requests.get(f"{BASE_URL}/workspaces/{workspace_id}/projects", headers=headers)
    projects_data = resp.json()
    
    projects = projects_data.get("data", projects_data) if isinstance(projects_data, dict) else projects_data
    if not projects:
        print("Creating project...")
        payload = {
            "name": "test project",
            "description": "test",
            "objective": "test",
            "target_audience": "test"
        }
        resp = requests.post(f"{BASE_URL}/workspaces/{workspace_id}/projects", headers=headers, json=payload)
        if not resp.ok:
            print("Failed to create project", resp.text)
            sys.exit(1)
        project_id = resp.json()["data"]["id"]
    else:
        project_id = projects[0]["id"]
    
    payload = {
        "workspace_id": workspace_id,
        "project_id": project_id,
        "platform": "X / Twitter",
        "content_type": "Thread",
        "user_request": "Which books contain ancient stories about gods like Shiva and Vishnu?",
        "tone": "Professional",
        "language": "English"
    }
    
    print("Triggering generate...")
    resp = requests.post(f"{BASE_URL}/content/generate", headers=headers, json=payload)
    print("Status code:", resp.status_code)
    print("Response:", resp.text)

if __name__ == "__main__":
    main()
