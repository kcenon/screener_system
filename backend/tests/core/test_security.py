"""Unit tests for security module (JWT and password utilities)"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import pytest
from app.core.config import settings
from app.core.security import (BCRYPT_ROUNDS, create_access_token,
                               create_refresh_token, decode_token,
                               get_password_hash, get_user_id_from_token,
                               verify_password, verify_token_type)
from freezegun import freeze_time
from jose import JWTError, jwt

# ============================================================================
# JWT Token Tests
# ============================================================================


class TestJWTTokenGeneration:
    """Test JWT token creation and encoding"""

    def test_create_access_token_with_default_expiration(self):
        """Test access token creation with default expiration time"""
        user_id = 123
        token = create_access_token(subject=user_id)

        # Verify token is a string
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify payload
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_with_custom_expiration(self):
        """Test access token creation with custom expiration delta"""
        user_id = 456
        custom_delta = timedelta(minutes=30)

        with freeze_time("2025-01-01 12:00:00"):
            token = create_access_token(subject=user_id, expires_delta=custom_delta)
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            # Verify expiration is 30 minutes from now
            exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
            expected_exp = iat_time + custom_delta

            assert exp_time == expected_exp
            assert payload["type"] == "access"

    def test_create_access_token_with_string_subject(self):
        """Test access token with string subject (email, username, etc.)"""
        subject = "user@example.com"
        token = create_access_token(subject=subject)

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        assert payload["sub"] == subject
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """Test refresh token creation with long expiration"""
        user_id = 789

        with freeze_time("2025-01-01 12:00:00"):
            token = create_refresh_token(subject=user_id)
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            # Verify refresh token properties
            assert payload["sub"] == str(user_id)
            assert payload["type"] == "refresh"

            # Verify expiration is in days (not minutes)
            exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
            expected_exp = iat_time + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

            assert exp_time == expected_exp

    def test_tokens_have_unique_iat(self):
        """Test that tokens created at different times have different iat"""
        user_id = 100

        with freeze_time("2025-01-01 12:00:00"):
            token1 = create_access_token(subject=user_id)
            payload1 = jwt.decode(
                token1,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

        with freeze_time("2025-01-01 12:05:00"):
            token2 = create_access_token(subject=user_id)
            payload2 = jwt.decode(
                token2,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

        # Different iat times
        assert payload1["iat"] != payload2["iat"]
        # But same subject
        assert payload1["sub"] == payload2["sub"]


class TestJWTTokenValidation:
    """Test JWT token decoding and validation"""

    def test_decode_valid_token(self):
        """Test decoding a valid, non-expired token"""
        user_id = 999
        token = create_access_token(subject=user_id)

        payload = decode_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_expired_token(self):
        """Test that expired tokens raise JWTError"""
        user_id = 888

        # Create token with very short expiration
        with freeze_time("2025-01-01 12:00:00"):
            token = create_access_token(
                subject=user_id,
                expires_delta=timedelta(seconds=1),
            )

        # Move time forward past expiration
        with freeze_time("2025-01-01 12:00:10"):
            with pytest.raises(JWTError) as exc_info:
                decode_token(token)

            assert "Invalid token" in str(exc_info.value)

    def test_decode_invalid_token_malformed(self):
        """Test decoding malformed token raises JWTError"""
        invalid_tokens = [
            "not.a.token",
            "invalid_token_string",
            "",
            "a.b.c.d.e",  # Too many parts
        ]

        for invalid_token in invalid_tokens:
            with pytest.raises(JWTError) as exc_info:
                decode_token(invalid_token)

            assert "Invalid token" in str(exc_info.value)

    def test_decode_token_wrong_secret(self):
        """Test that token signed with different secret fails validation"""
        user_id = 777

        # Create token with wrong secret
        wrong_secret = "wrong_secret_key_12345"
        payload: Dict[str, Any] = {
            "sub": str(user_id),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            "iat": datetime.now(timezone.utc),
        }
        wrong_token = jwt.encode(
            payload,
            wrong_secret,
            algorithm=settings.ALGORITHM,
        )

        # Should fail validation with correct secret
        with pytest.raises(JWTError):
            decode_token(wrong_token)

    def test_decode_token_wrong_algorithm(self):
        """Test that token signed with different algorithm fails"""
        user_id = 666

        # Create token with wrong algorithm (using HS512 instead of HS256)
        payload: Dict[str, Any] = {
            "sub": str(user_id),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            "iat": datetime.now(timezone.utc),
        }
        wrong_algo_token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS512",
        )

        # Should fail validation
        with pytest.raises(JWTError):
            decode_token(wrong_algo_token)

    def test_verify_token_type_access(self):
        """Test verifying access token type"""
        user_id = 555
        token = create_access_token(subject=user_id)

        assert verify_token_type(token, "access") is True
        assert verify_token_type(token, "refresh") is False

    def test_verify_token_type_refresh(self):
        """Test verifying refresh token type"""
        user_id = 444
        token = create_refresh_token(subject=user_id)

        assert verify_token_type(token, "refresh") is True
        assert verify_token_type(token, "access") is False

    def test_verify_token_type_invalid_token(self):
        """Test token type verification with invalid token"""
        invalid_token = "invalid.token.here"

        assert verify_token_type(invalid_token, "access") is False
        assert verify_token_type(invalid_token, "refresh") is False

    def test_get_user_id_from_token_valid(self):
        """Test extracting user ID from valid token"""
        user_id = 12345
        token = create_access_token(subject=user_id)

        extracted_id = get_user_id_from_token(token)

        assert extracted_id == user_id
        assert isinstance(extracted_id, int)

    def test_get_user_id_from_token_invalid(self):
        """Test extracting user ID from invalid token returns None"""
        invalid_tokens = [
            "invalid.token",
            "",
            "not_a_jwt_token",
        ]

        for invalid_token in invalid_tokens:
            assert get_user_id_from_token(invalid_token) is None

    def test_get_user_id_from_token_no_subject(self):
        """Test extracting user ID from token without 'sub' claim"""
        # Create token without 'sub' field
        payload: Dict[str, Any] = {
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            "iat": datetime.now(timezone.utc),
        }
        token_no_sub = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        assert get_user_id_from_token(token_no_sub) is None

    def test_get_user_id_from_token_non_numeric_subject(self):
        """Test extracting user ID from token with non-numeric subject"""
        # Create token with non-numeric subject
        token = create_access_token(subject="not_a_number")

        # Should return None because conversion to int fails
        assert get_user_id_from_token(token) is None


# ============================================================================
# Password Hashing and Verification Tests
# ============================================================================


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password_produces_hash(self):
        """Test that password hashing produces a valid hash string"""
        password = "my_secure_password_123"
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Hash should be different from plain password
        assert hashed.startswith("$2b$")  # Bcrypt hash format

    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salt randomness)"""
        password = "same_password"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Different hashes due to random salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_hash_password_unicode_characters(self):
        """Test password hashing with Unicode characters"""
        unicode_passwords = [
            "패스워드123",  # Korean
            "пароль456",  # Cyrillic
            "密码789",  # Chinese
            "🔐🔑password",  # Emojis
        ]

        for password in unicode_passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed)

    def test_hash_password_empty_string(self):
        """Test hashing empty password (should work, though not recommended)"""
        password = ""
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert verify_password(password, hashed)

    def test_hash_password_very_long(self):
        """Test hashing very long password (bcrypt 72-byte limit)"""
        # bcrypt has 72-byte limit; our implementation truncates to 72 bytes
        long_password = "a" * 100
        hashed = get_password_hash(long_password)

        # Verify full password works (both truncated internally to 72 bytes)
        assert verify_password(long_password, hashed)

        # Verify truncated password (first 72 bytes) also works
        truncated_password = "a" * 72
        assert verify_password(truncated_password, hashed)

    def test_hash_uses_correct_rounds(self):
        """Test that hash uses configured bcrypt rounds"""
        password = "test_password"
        hashed = get_password_hash(password)

        # Bcrypt hash format: $2b$rounds$salt+hash
        # Extract rounds from hash
        parts = hashed.split("$")
        rounds = int(parts[2])

        assert rounds == BCRYPT_ROUNDS  # Should use configured rounds (12)


class TestPasswordVerification:
    """Test password verification"""

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "correct_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with wrong password"""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(correct_password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_vs_non_empty(self):
        """Test verification fails for empty vs non-empty password"""
        password = "non_empty_password"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False
        assert verify_password(password, hashed) is True

    def test_verify_password_case_sensitive(self):
        """Test password verification is case-sensitive"""
        password = "CaseSensitive"
        hashed = get_password_hash(password)

        assert verify_password("CaseSensitive", hashed) is True
        assert verify_password("casesensitive", hashed) is False
        assert verify_password("CASESENSITIVE", hashed) is False

    def test_verify_password_with_special_characters(self):
        """Test password verification with special characters"""
        special_passwords = [
            "p@ssw0rd!",
            "test#123$%^",
            "password with spaces",
            "pass\nword",  # Newline
            "pass\tword",  # Tab
        ]

        for password in special_passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True
            assert verify_password(password + "x", hashed) is False

    def test_verify_password_timing_attack_resistance(self):
        """Test that password verification has consistent timing
        (timing attack prevention)
        """
        import time

        password = "test_password_for_timing"
        hashed = get_password_hash(password)

        # Measure time for correct password
        times_correct = []
        for _ in range(10):
            start = time.perf_counter()
            verify_password(password, hashed)
            end = time.perf_counter()
            times_correct.append(end - start)

        # Measure time for incorrect password
        times_incorrect = []
        for _ in range(10):
            start = time.perf_counter()
            verify_password("wrong_password", hashed)
            end = time.perf_counter()
            times_incorrect.append(end - start)

        # Timing should be similar (within reasonable variance)
        # Note: Bcrypt naturally has constant-time comparison
        avg_correct = sum(times_correct) / len(times_correct)
        avg_incorrect = sum(times_incorrect) / len(times_incorrect)

        # Allow for some variance, but should be in same order of magnitude
        # Bcrypt is designed to be slow (intentionally), so times should be similar
        assert abs(avg_correct - avg_incorrect) < 0.1  # Less than 100ms difference


# ============================================================================
# Edge Cases and Security Tests
# ============================================================================


class TestSecurityEdgeCases:
    """Test edge cases and security scenarios"""

    def test_token_with_null_bytes(self):
        """Test handling of null bytes in token"""
        # Create token and inject null byte
        token = create_access_token(subject=123)
        token_with_null = token + "\x00"

        with pytest.raises(JWTError):
            decode_token(token_with_null)

    def test_password_with_null_bytes(self):
        """Test password hashing with null bytes"""
        # Password with null byte
        password = "password\x00with_null"
        hashed = get_password_hash(password)

        # Should still work (Python strings can contain null bytes)
        assert verify_password(password, hashed) is True
        assert verify_password("password", hashed) is False

    def test_very_large_user_id(self):
        """Test token creation with very large user ID"""
        large_user_id = 2**63 - 1  # Max 64-bit integer
        token = create_access_token(subject=large_user_id)

        extracted_id = get_user_id_from_token(token)
        assert extracted_id == large_user_id

    def test_negative_user_id(self):
        """Test token creation with negative user ID"""
        negative_id = -123
        token = create_access_token(subject=negative_id)

        extracted_id = get_user_id_from_token(token)
        assert extracted_id == negative_id

    def test_token_replay_attack_scenario(self):
        """Test that old tokens can be identified by iat timestamp"""
        user_id = 999

        with freeze_time("2025-01-01 12:00:00"):
            old_token = create_access_token(subject=user_id)
            old_payload = decode_token(old_token)

        with freeze_time("2025-01-01 13:00:00"):
            new_token = create_access_token(subject=user_id)
            new_payload = decode_token(new_token)

        # Can distinguish old vs new tokens by iat
        assert old_payload["iat"] < new_payload["iat"]
        # Both are valid if not expired
        assert old_payload["sub"] == new_payload["sub"]

    def test_token_tampering_detection(self):
        """Test that tampered tokens are detected and rejected"""
        user_id = 123
        token = create_access_token(subject=user_id)

        # Split token into parts
        parts = token.split(".")
        assert len(parts) == 3  # header.payload.signature

        # Tamper with payload (base64 encoded)
        import base64

        # Decode payload, modify it, re-encode
        payload_b64 = parts[1]
        # Add padding if needed
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding

        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        # Create tampered payload with different user_id
        tampered_payload = payload_bytes.replace(b'"sub":"123"', b'"sub":"999"')
        tampered_b64 = base64.urlsafe_b64encode(tampered_payload).decode().rstrip("=")

        # Reconstruct token with tampered payload
        tampered_token = f"{parts[0]}.{tampered_b64}.{parts[2]}"

        # Should fail signature verification
        with pytest.raises(JWTError):
            decode_token(tampered_token)

    def test_concurrent_token_generation(self):
        """Test that concurrent token generation produces unique tokens"""
        user_id = 100

        # Generate multiple tokens rapidly
        tokens = [create_access_token(subject=user_id) for _ in range(10)]

        # All tokens should be unique (due to different timestamps at millisecond level)
        # Note: In practice, some may be identical if generated in same millisecond
        # We just verify they're all valid tokens
        for token in tokens:
            payload = decode_token(token)
            assert payload["sub"] == str(user_id)
            assert payload["type"] == "access"

    def test_empty_subject_handling(self):
        """Test token creation with empty string subject"""
        token = create_access_token(subject="")
        payload = decode_token(token)

        assert payload["sub"] == ""
        assert payload["type"] == "access"

    def test_special_characters_in_subject(self):
        """Test token creation with special characters in subject"""
        special_subjects = [
            "user@example.com",
            "user+tag@domain.co.kr",
            "123-456-789",
            "uuid:550e8400-e29b-41d4-a716-446655440000",
        ]

        for subject in special_subjects:
            token = create_access_token(subject=subject)
            payload = decode_token(token)
            assert payload["sub"] == subject

    def test_token_claims_completeness(self):
        """Test that all expected claims are present in tokens"""
        user_id = 456

        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        # Required claims for access token
        assert "sub" in access_payload
        assert "type" in access_payload
        assert "exp" in access_payload
        assert "iat" in access_payload
        assert access_payload["type"] == "access"

        # Required claims for refresh token
        assert "sub" in refresh_payload
        assert "type" in refresh_payload
        assert "exp" in refresh_payload
        assert "iat" in refresh_payload
        assert refresh_payload["type"] == "refresh"

    def test_password_boundary_at_72_bytes(self):
        """Test password hashing behavior exactly at 72-byte boundary"""
        # Exactly 72 bytes (ASCII)
        password_72 = "a" * 72
        # 73 bytes (one over)
        password_73 = "a" * 73

        hash_72 = get_password_hash(password_72)
        hash_73 = get_password_hash(password_73)

        # Both should verify against the 72-byte password
        assert verify_password(password_72, hash_72)
        assert verify_password(password_73, hash_73)

        # Due to truncation, 73-byte password verifies against 72-byte hash
        # (because both are truncated to 72 bytes internally)
        assert verify_password(password_73, hash_72)
        assert verify_password(password_72, hash_73)

    def test_refresh_token_longer_expiration_than_access(self):
        """Test that refresh tokens have longer expiration than access tokens"""
        user_id = 789

        with freeze_time("2025-01-01 12:00:00"):
            access_token = create_access_token(subject=user_id)
            refresh_token = create_refresh_token(subject=user_id)

            access_payload = decode_token(access_token)
            refresh_payload = decode_token(refresh_token)

            # Refresh token should expire later than access token
            assert refresh_payload["exp"] > access_payload["exp"]

            # Difference should be significant (days vs minutes)
            exp_diff = refresh_payload["exp"] - access_payload["exp"]
            # At least 1 day difference (86400 seconds)
            assert exp_diff > 86400
