import os
import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

def get_google_login_url():
    return f"{API_BASE_URL}/auth/google/login"

def fetch_user_profile(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def update_user_profile(jwt_token: str, name: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"name": name}
    response = requests.patch(f"{API_BASE_URL}/auth/me", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_dashboard_metrics(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/dashboard/metrics", headers=headers)
    if response.status_code == 200:
        return response.json()
    return {}

def fetch_dashboard_charts(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/dashboard/charts", headers=headers)
    if response.status_code == 200:
        return response.json()
    return {"usage": [], "distribution": []}

def fetch_dashboard_activity(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/dashboard/activity", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def fetch_conversations(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/chat/conversations", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def fetch_messages(jwt_token: str, conv_id: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/chat/conversations/{conv_id}/messages", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def generate_code(jwt_token: str, prompt: str, conv_id: str = None):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"prompt": prompt}
    if conv_id:
        data["conversation_id"] = conv_id
        
    response = requests.post(f"{API_BASE_URL}/agents/code", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    return None

def perform_search(jwt_token: str, query: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"query": query}
    response = requests.post(f"{API_BASE_URL}/agents/search", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    return None

def generate_document(jwt_token: str, prompt: str, format: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"prompt": prompt}
    endpoint = f"{API_BASE_URL}/agents/documents/{format}"
    response = requests.post(endpoint, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_documents(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/agents/documents/history", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def generate_image(jwt_token: str, prompt: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"prompt": prompt}
    response = requests.post(f"{API_BASE_URL}/agents/image", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_images(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/agents/image/history", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def upload_rag_document(jwt_token: str, file_path: str, filename: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    with open(file_path, "rb") as f:
        files = {"file": (filename, f, "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/agents/rag/upload", headers=headers, files=files)
    if response.status_code == 200:
        return response.json()
    return None

def query_rag_document(jwt_token: str, document_id: str, query: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"document_id": document_id, "query": query}
    response = requests.post(f"{API_BASE_URL}/agents/rag/query", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_rag_documents(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/agents/rag/documents", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def fetch_balance(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/billing/balance", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_transactions(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/billing/transactions", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []
