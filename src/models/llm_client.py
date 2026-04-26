"""
LLM Client abstraction layer - supports multiple providers
"""
import json
from typing import Optional
from config import HF_API_TOKEN, LLM_MODEL, LLM_API_PROVIDER


class BaseLLMClient:
    """Base LLM client interface"""

    def __init__(self):
        self.model = LLM_MODEL
        self.provider = LLM_API_PROVIDER

    def generate(self, prompt: str, max_tokens: int = 1024, **kwargs) -> str:
        """Generate text from prompt"""
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing (used when no API token available)"""

    def __init__(self):
        super().__init__()
        self.provider = "mock"

    def generate(self, prompt: str, max_tokens: int = 1024, **kwargs) -> str:
        """Return mock responses based on prompt type"""
        if "assess" in prompt.lower() and "python" in prompt.lower():
            return json.dumps({
                "proficiency_level": "Intermediate",
                "confidence_score": 0.75,
                "assessment_notes": "Demonstrated understanding of OOP and decorators",
                "evidence": ["Showed practical debugging skills", "Knows async/await patterns"],
                "questions": [
                    "Tell me about your experience with Python decorators",
                    "How would you optimize a slow pandas operation?"
                ]
            })
        elif "learning" in prompt.lower():
            return json.dumps({
                "resources": [
                    {"title": "Advanced Python Patterns", "type": "course", "hours": 12, "url": ""},
                    {"title": "Effective Python by Brett Slatkin", "type": "book", "hours": 8},
                    {"title": "Real Python Advanced Topics", "type": "tutorial", "hours": 6}
                ],
                "learning_path": "Start with patterns course, then read the book, practice with projects"
            })
        else:
            return json.dumps({"response": "Assessment in progress"})


class HuggingFaceClient(BaseLLMClient):
    """Hugging Face Inference API client"""

    def __init__(self, api_token: Optional[str] = None):
        super().__init__()
        self.api_token = api_token or HF_API_TOKEN
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"

        if not self.api_token:
            raise ValueError(
                "HuggingFace API token not found. "
                "Set HF_API_TOKEN environment variable or pass api_token parameter."
            )

    def generate(self, prompt: str, max_tokens: int = 1024, **kwargs) -> str:
        """Generate text using HuggingFace API"""
        import requests

        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_tokens,
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95)
            }
        }

        response = requests.post(self.api_url, headers=headers, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"API Error: {response.status_code} - {response.text}")

        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "")
        return ""


class OllamaClient(BaseLLMClient):
    """Ollama local client"""

    def __init__(self, model: Optional[str] = None, base_url: str = "http://localhost:11434"):
        super().__init__()
        self.model = model or self.model
        self.base_url = base_url
        self.provider = "ollama"

    def generate(self, prompt: str, max_tokens: int = 1024, **kwargs) -> str:
        """Generate text using Ollama"""
        import requests

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "num_predict": max_tokens,
            "temperature": kwargs.get("temperature", 0.7)
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"Ollama Error: {response.status_code}")

        result = response.json()
        return result.get("response", "")


def get_llm_client() -> BaseLLMClient:
    """Factory function to get appropriate LLM client"""
    try:
        if LLM_API_PROVIDER == "huggingface" and HF_API_TOKEN:
            return HuggingFaceClient(HF_API_TOKEN)
        elif LLM_API_PROVIDER == "ollama":
            return OllamaClient()
        else:
            # Default to mock client for demo purposes
            return MockLLMClient()
    except Exception as e:
        print(f"Warning: Could not initialize {LLM_API_PROVIDER}, falling back to mock: {e}")
        return MockLLMClient()
