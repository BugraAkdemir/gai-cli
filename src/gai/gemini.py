"""
Gemini API integration module.

This module is responsible for:
- Reading the GEMINI_API_KEY from environment
- Initializing the Google Generative AI client
- Sending prompts and returning responses
"""

import os
from typing import Optional

from google import genai
from google.genai.types import GenerateContentConfig

from gai import config

class GeminiError(Exception):
    """Base exception for Gemini-related errors."""
    pass


class APIKeyMissingError(GeminiError):
    """Raised when the GEMINI_API_KEY environment variable is not set."""
    pass

class InvalidAPIKeyError(GeminiError):
    """Raised when the API key is rejected by the service."""
    pass


def _get_api_key() -> str:
    """
    Retrieve the API key from config/env.
    
    Returns:
        str: The API key.
        
    Raises:
        APIKeyMissingError: If no key is found.
    """
    api_key = config.get_api_key()
    if not api_key:
        raise APIKeyMissingError(
            "API key not found. Please verify your configuration."
        )
    return api_key

def validate_api_key() -> bool:
    """
    Validate the current API key by making a lightweight request.
    
    Returns:
        bool: True if valid, False otherwise.
        
    Raises:
        APIKeyMissingError: If no key is configured.
    """
    api_key = _get_api_key()
    try:
        client = genai.Client(api_key=api_key)
        # Simple test: list models (lightweight) or a tiny prompt
        # Listing models is usually free and fast auth check
        try:
             # Just checking if we can init the model object might not trigger auth until send
             # Let's try a very basic generate
             client.models.generate_content(
                model=config.get_model(),
                contents="test"
             )
             return True
        except Exception:
             # In some SDK versions, auth error might raise immediately
             # But generally we catch request errors
             return False
    except Exception:
        return False


def generate_response(
    prompt: str,
    history: Optional[list] = None,
    system_instruction: Optional[str] = None,
    model_name: Optional[str] = None
) -> str:
    """
    Generate a response from the Gemini API.
    Supports multi-turn history and system instructions.
    """
    # Get API key
    api_key = _get_api_key()
    
    if model_name is None:
        model_name = config.get_model()
    
    try:
        # Initialize the client
        client = genai.Client(api_key=api_key)
        
        # Prepare contents
        contents = []
        if history:
            for turn in history:
                # API expects 'model' role for assistant
                role = "model" if turn.get("role") == "assistant" else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": turn.get("content", "")}]
                })
        
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        # Config with system instruction
        config_args = {}
        if system_instruction:
            config_args["system_instruction"] = system_instruction
            
        # Generate response
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config_args
        )
        
        # Extract and return text
        if response.text:
            return response.text
        else:
            raise GeminiError("Received empty response from Gemini API")
            
    except Exception as e:
        msg = str(e).lower()
        
        # Check for quota/rate limit errors first
        if "quota" in msg or "rate limit" in msg or "resource_exhausted" in msg:
            raise GeminiError(f"API Quota/Rate Limit Exceeded: {str(e)}\n\nTry switching models with /model command or wait a few minutes.")
        
        # Only treat actual authentication failures as invalid API key
        # Be very specific to avoid false positives from rate limiting, quota, etc.
        if "api_key_invalid" in msg or ("403" in msg and "api key" in msg):
            raise InvalidAPIKeyError(f"Invalid API Key: {str(e)}")
        
        # Catch other auth-related but not necessarily key issues
        if "401" in msg or "unauthenticated" in msg:
            raise InvalidAPIKeyError(f"Authentication failed: {str(e)}")
            
        if isinstance(e, (APIKeyMissingError, GeminiError)):
            raise
        raise GeminiError(f"Error communicating with Gemini API: {str(e)}") from e


class ChatSession:
    """
    A wrapper around the Gemini chat session.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.api_key = _get_api_key()
        if model_name is None:
            self.model_name = config.get_model()
        else:
            self.model_name = model_name
            
        self.client = genai.Client(api_key=self.api_key)
        self.chat = self.client.chats.create(model=self.model_name)
        
    def send_message(self, message: str) -> str:
        """
        Send a message to the chat session and get the response.
        """
        try:
            response = self.chat.send_message(message)
            if response.text:
                return response.text
            return ""
        except Exception as e:
            msg = str(e)
            if "403" in msg or "401" in msg or "PERMISSION_DENIED" in msg:
                 raise InvalidAPIKeyError("Invalid API Key.")
            raise GeminiError(f"Error in chat session: {str(e)}") from e

