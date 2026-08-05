import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")
# Use a browser-accessible URL for anchor links
BROWSER_API_BASE_URL = os.environ.get("BROWSER_API_BASE_URL", "http://localhost:8000/api/v1")

def get_google_login_url():
    return f"{BROWSER_API_BASE_URL}/auth/google/login"

def get_dev_login_url():
    return f"{BROWSER_API_BASE_URL}/auth/dev-login"

@st.cache_data(ttl=60)
def fetch_user_profile(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

def update_user_profile(jwt_token: str, name: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"name": name}
    try:
        response = requests.patch(f"{API_BASE_URL}/auth/me", headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

@st.cache_data(ttl=15)
def fetch_dashboard_metrics(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/metrics", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return {}

@st.cache_data(ttl=15)
def fetch_dashboard_charts(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/charts", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return {"usage": [], "distribution": []}

@st.cache_data(ttl=15)
def fetch_dashboard_activity(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/activity", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

@st.cache_data(ttl=15)
def fetch_conversations(jwt_token: str, agent_type: str = None):
    url = f"{API_BASE_URL}/chat/conversations"
    if agent_type:
        url += f"?agent_type={agent_type}"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def fetch_messages(jwt_token: str, conv_id: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/chat/conversations/{conv_id}/messages", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def generate_code(jwt_token: str, prompt: str, conv_id: str = None):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"prompt": prompt}
    if conv_id:
        data["conversation_id"] = conv_id

    try:
        response = requests.post(f"{API_BASE_URL}/agents/code", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 402:
            return {"error": "Insufficient credits to perform this action."}
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def perform_search(jwt_token: str, query: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"query": query}
    try:
        response = requests.post(f"{API_BASE_URL}/agents/search", headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 402:
            return {"error": "Insufficient credits to perform this search."}
        else:
            try:
                err_msg = response.json().get("detail", response.text)
            except Exception:
                err_msg = response.text
            return {"error": f"Search failed ({response.status_code}): {err_msg}"}
    except requests.exceptions.Timeout:
        return {"error": "The search request timed out. The AI took too long to synthesize an answer. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error occurred: {e!s}"}

def generate_document(jwt_token: str, prompt: str, format: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"prompt": prompt}
    endpoint = f"{API_BASE_URL}/agents/documents/{format}"
    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

@st.cache_data(ttl=15)
def fetch_documents(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/agents/documents/history", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def generate_image(jwt_token: str, prompt: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"prompt": prompt}
    try:
        response = requests.post(f"{API_BASE_URL}/agents/image", headers=headers, json=data, timeout=45)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 402:
            return {"error": "Insufficient credits to generate this image."}
        else:
            return {"error": f"Image generation failed ({response.status_code}): {response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "Image generation timed out. Please try again."}
    except Exception as e:
        return {"error": f"Error: {e!s}"}

@st.cache_data(ttl=15)
def fetch_images(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/agents/image/history", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def upload_rag_document(jwt_token: str, file_path: str, filename: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        with open(file_path, "rb") as f:
            files = {"file": (filename, f, "application/pdf")}
            response = requests.post(f"{API_BASE_URL}/agents/rag/upload", headers=headers, files=files, timeout=60)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 402:
            return {"error": "Insufficient credits to process document."}
        else:
            return {"error": f"Upload failed ({response.status_code}): {response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "Upload timed out. The document might be too large."}
    except Exception as e:
        return {"error": f"Error: {e!s}"}

def query_rag_document(jwt_token: str, document_id: str, query: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"document_id": document_id, "query": query}
    try:
        response = requests.post(f"{API_BASE_URL}/agents/rag/query", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 402:
            return {"error": "Insufficient credits to perform this query."}
        else:
            return {"error": f"Query failed ({response.status_code}): {response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "Query timed out. Please try again."}
    except Exception as e:
        return {"error": f"Error: {e!s}"}

@st.cache_data(ttl=15)
def fetch_rag_documents(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/agents/rag/documents", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

@st.cache_data(ttl=60)
def fetch_balance(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/billing/balance", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

def fetch_transactions(jwt_token: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/billing/transactions", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def enhance_document_prompt(jwt_token: str, user_prompt: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {
        "content": f"Enhance this document prompt to be extremely detailed, professional, and comprehensive. Only return the final improved prompt text, no intro, no conversational filler:\n\n{user_prompt}",
        "agent_type": "chat"
    }

    try:
        response = requests.post(f"{API_BASE_URL}/chat/message", headers=headers, json=data, stream=True, timeout=30)
        enhanced = ""
        if response.status_code == 200:
            import json
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('data:'):
                        try:
                            chunk = json.loads(decoded[5:])
                            if "content" in chunk:
                                enhanced += chunk["content"]
                            elif "conversation_id" in chunk:
                                pass
                        except Exception:
                            pass
            return enhanced.strip()
    except requests.exceptions.RequestException:
        pass
    return None

def delete_document(jwt_token: str, file_id: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.delete(f"{API_BASE_URL}/agents/documents/{file_id}", headers=headers, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def delete_image(jwt_token: str, artifact_id: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.delete(f"{API_BASE_URL}/agents/image/{artifact_id}", headers=headers, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def rename_document(jwt_token: str, file_id: str, new_name: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {"new_name": new_name}
    try:
        response = requests.patch(f"{API_BASE_URL}/agents/documents/{file_id}/rename", headers=headers, json=data, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def duplicate_document(jwt_token: str, file_id: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.post(f"{API_BASE_URL}/agents/documents/{file_id}/duplicate", headers=headers, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def search_dashboard(jwt_token: str, query: str):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    params = {"q": query}
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/search", headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []
