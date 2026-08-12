import logging
import base64
import json
import os
import pytest

from my_app.server import credential_integration
from my_app.server.encryption_service import CredentialEncryptionService
from pathlib import Path
from my_app.server.app import log_ai_call
from my_app.config.settings import settings
from my_app.server.api_key_manager import validate_api_key
from my_app.server.main import validate_production_security_config

def test_development_api_key_requires_explicit_configuration(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """The old predictable 'dev-bypass' value must not work by default."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    monkeypatch.setenv("DEV_USER_ID", "dev-test-user")
    monkeypatch.delenv("DEV_API_KEY", raising=False)

    missing_oauth_file = tmp_path / "oauth.json"

    assert validate_api_key("dev-bypass", missing_oauth_file) is None

    monkeypatch.setenv("DEV_API_KEY", "explicit-test-key")

    assert validate_api_key("dev-bypass", missing_oauth_file) is None
    assert (
        validate_api_key("explicit-test-key", missing_oauth_file)
        == "dev-test-user"
    )
def test_api_key_validation_accepts_valid_key_and_rejects_invalid_key(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Stored API-key hashes should validate without storing plaintext keys."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    valid_key = "sk_live_FAKE_TEST_KEY_ONLY_123456"
    oauth_file = tmp_path / "oauth.json"

    oauth_file.write_text(
        json.dumps(
            {
                "users": [
                    {
                        "user_id": "security-test-user",
                        "api_key": {
                            "key_hash": __import__(
                                "my_app.server.api_key_manager",
                                fromlist=["hash_api_key"],
                            ).hash_api_key(valid_key)
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assert validate_api_key(valid_key, oauth_file) == "security-test-user"
    assert validate_api_key("wrong-test-key", oauth_file) is None
def test_production_startup_requires_encryption_secrets(
    monkeypatch,
) -> None:
    """Production startup must fail when required encryption secrets are missing."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.delenv("MASTER_ENCRYPTION_KEY", raising=False)
    monkeypatch.delenv("ENCRYPTION_SALT", raising=False)
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", "fake-jwt-secret-for-test-only")

    with pytest.raises(RuntimeError) as exc_info:
        validate_production_security_config()

    message = str(exc_info.value)

    assert "MASTER_ENCRYPTION_KEY" in message
    assert "ENCRYPTION_SALT" in message


def test_production_startup_accepts_valid_security_config(
    monkeypatch,
) -> None:
    """Production startup validation should pass with explicit fake test secrets."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setenv(
        "MASTER_ENCRYPTION_KEY",
        "fake-master-key-for-test-only",
    )
    monkeypatch.setenv(
        "ENCRYPTION_SALT",
        "fake-encryption-salt-for-test-only",
    )
    monkeypatch.setattr(
        settings,
        "JWT_SECRET_KEY",
        "fake-jwt-secret-for-test-only",
    )

    validate_production_security_config()

def test_ai_logging_excludes_prompt_and_response_content(caplog) -> None:
    """AI logs must contain metadata only, not prompt or response content."""
    fake_prompt = "FAKE_SECRET_PROMPT_12345"
    fake_response = "FAKE_SECRET_RESPONSE_67890"

    with caplog.at_level(logging.INFO):
        log_ai_call(
            user_id="test-user",
            model="test-model",
            messages=[{"role": "user", "content": fake_prompt}],
            result={"content": fake_response, "tool_calls": []},
        )

    output = caplog.text

    assert fake_prompt not in output
    assert fake_response not in output
    assert "Message Count: 1" in output
    assert "User Message Count: 1" in output
def test_encryption_round_trip(monkeypatch) -> None:
    """Encrypted credentials should decrypt back to the original values."""
    monkeypatch.setenv(
        "MASTER_ENCRYPTION_KEY",
        "fake-master-key-for-encryption-test-only",
    )
    monkeypatch.setenv(
        "ENCRYPTION_SALT",
        "fake-encryption-salt-for-test-only",
    )

    service = CredentialEncryptionService()

    original = {
        "access_token": "FAKE_ACCESS_TOKEN",
        "refresh_token": "FAKE_REFRESH_TOKEN",
    }

    encrypted = service.encrypt_credentials(original)
    decrypted = service.decrypt_credentials(encrypted)

    assert encrypted != str(original).encode()
    assert decrypted == original


def test_tampered_ciphertext_is_rejected(monkeypatch) -> None:
    """AES-GCM authentication must reject modified ciphertext."""
    monkeypatch.setenv(
        "MASTER_ENCRYPTION_KEY",
        "fake-master-key-for-encryption-test-only",
    )
    monkeypatch.setenv(
        "ENCRYPTION_SALT",
        "fake-encryption-salt-for-test-only",
    )

    service = CredentialEncryptionService()
    encrypted = bytearray(
        service.encrypt_credentials({"token": "FAKE_TOKEN"})
    )

    encrypted[-1] ^= 1

    with pytest.raises(ValueError, match="Decryption failed"):
        service.decrypt_credentials(bytes(encrypted))

def test_encryption_service_requires_master_key(monkeypatch) -> None:
    """Encryption must fail closed when the master key is missing."""
    monkeypatch.delenv("MASTER_ENCRYPTION_KEY", raising=False)
    monkeypatch.setenv(
        "ENCRYPTION_SALT",
        "fake-encryption-salt-for-test-only",
    )

    with pytest.raises(
        ValueError,
        match="MASTER_ENCRYPTION_KEY must be set",
    ):
        CredentialEncryptionService()

def test_google_credentials_use_secure_storage_helper(monkeypatch) -> None:
    """Google OAuth credentials must be passed to the encrypted credential manager."""
    stored_calls = []

    class FakeCredentialManager:
        def store_credentials(self, **kwargs):
            stored_calls.append(kwargs)
            return True

    monkeypatch.setattr(
        credential_integration,
        "get_credential_manager",
        lambda: FakeCredentialManager(),
    )

    fake_credentials = {
        "token": "FAKE_GOOGLE_TOKEN_TEST_ONLY",
        "refresh_token": "FAKE_REFRESH_TOKEN_TEST_ONLY",
    }

    result = credential_integration.store_google_credentials(
        user_id="security-test-user",
        credential_data=fake_credentials,
        email="test@example.com",
        scopes=["scope-a"],
        connected_at="2026-08-03T12:00:00",
    )

    assert result is True
    assert len(stored_calls) == 1

    stored = stored_calls[0]

    assert stored["service_name"] == "google"
    assert stored["credential_type"] == "oauth"
    assert stored["credential_data"] == fake_credentials
    assert stored["created_by"] == "security-test-user"
    assert stored["metadata"]["email"] == "test@example.com"

def test_oauth_callback_does_not_persist_plaintext_google_credentials() -> None:
    """OAuth callback source must not write Google credentials into oauth.json."""
    app_source = (
        Path(__file__).parents[1]
        / "my_app"
        / "server"
        / "app.py"
    ).read_text(encoding="utf-8")

    assert '"credentials": credentials.to_json()' not in app_source
    assert '"credential_storage": "encrypted_dynamodb"' in app_source
    assert "store_google_credentials(" in app_source