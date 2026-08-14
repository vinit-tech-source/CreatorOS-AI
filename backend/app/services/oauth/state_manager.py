"""
app/services/oauth/state_manager.py

Manager for generating and validating OAuth state tokens.
Provides CSRF protection and prevents state reuse.
"""
import secrets
import time
from typing import Dict, Any, Optional
import uuid

# In-memory store for MVP. Production would use Redis or DB.
# Structure: { state_token: {"workspace_id": str, "platform": str, "expires_at": float} }
_state_store: Dict[str, Dict[str, Any]] = {}

# Default expiration for OAuth state (15 minutes)
STATE_EXPIRATION_SECONDS = 15 * 60

class OAuthStateManager:
    """
    Manages OAuth state generation, storage, and validation.
    """
    
    @classmethod
    def generate_state(cls, workspace_id: uuid.UUID, platform: str) -> str:
        """
        Generate a cryptographically secure state string and store its metadata.
        """
        # Cleanup expired states
        cls._cleanup_expired()
        
        state = secrets.token_urlsafe(32)
        _state_store[state] = {
            "workspace_id": str(workspace_id),
            "platform": platform,
            "expires_at": time.time() + STATE_EXPIRATION_SECONDS
        }
        return state
        
    @classmethod
    def validate_and_consume_state(cls, state: str) -> Optional[Dict[str, Any]]:
        """
        Validate a state token. If valid, consume it (prevents reuse) and return metadata.
        Returns None if invalid, expired, or already used.
        """
        cls._cleanup_expired()
        
        metadata = _state_store.pop(state, None)
        if not metadata:
            return None
            
        if time.time() > metadata["expires_at"]:
            return None
            
        return metadata
        
    @classmethod
    def _cleanup_expired(cls) -> None:
        """Remove expired state entries from memory."""
        current_time = time.time()
        expired_keys = [k for k, v in _state_store.items() if current_time > v["expires_at"]]
        for k in expired_keys:
            _state_store.pop(k, None)
