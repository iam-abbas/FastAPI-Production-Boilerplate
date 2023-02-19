from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from jose import JWTError, jwt

from core.security.jwt import JWTDecodeError, JWTHandler


class MockConfig:
    SECRET_KEY = "secret_key"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 10


@pytest.fixture
def mock_config():
    return MockConfig()


@pytest.fixture
def mock_payload():
    return {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}


@pytest.fixture
def mock_token(mock_payload, mock_config):
    expire = datetime.utcnow() + timedelta(minutes=mock_config.JWT_EXPIRE_MINUTES)
    payload = mock_payload.copy()
    payload.update({"exp": expire})
    return jwt.encode(
        payload, mock_config.SECRET_KEY, algorithm=mock_config.JWT_ALGORITHM
    )


@pytest.fixture
def mock_expired_token(mock_payload, mock_config):
    expire = (
        datetime.utcnow()
        - timedelta(minutes=mock_config.JWT_EXPIRE_MINUTES)
        - timedelta(seconds=10)
    )
    payload = mock_payload.copy()
    payload.update({"exp": expire})
    return jwt.encode(
        payload, mock_config.SECRET_KEY, algorithm=mock_config.JWT_ALGORITHM
    )


@pytest.fixture
def mock_decode_token(mock_config, mock_payload):
    return jwt.encode(
        mock_payload, mock_config.SECRET_KEY, algorithm=mock_config.JWT_ALGORITHM
    )


@pytest.fixture
def mock_handler(mock_config):
    jwt_handler = JWTHandler
    jwt_handler.secret_key = mock_config.SECRET_KEY
    jwt_handler.algorithm = mock_config.JWT_ALGORITHM
    jwt_handler.expire_minutes = mock_config.JWT_EXPIRE_MINUTES

    return jwt_handler


class TestJWTHandler:
    @patch("core.security.jwt.config", MagicMock(return_value=mock_config))
    def test_encode(self, mock_payload, mock_handler):
        token = mock_handler.encode(mock_payload)
        assert token is not None
        assert isinstance(token, str)

    @patch("core.security.jwt.config", MagicMock(return_value=mock_config))
    def test_decode(self, mock_token, mock_payload, mock_handler):
        decoded = mock_handler.decode(mock_token)
        assert decoded is not None
        assert isinstance(decoded, dict)
        assert decoded.pop("exp") is not None
        assert decoded == mock_payload

    @patch("core.security.jwt.config", MagicMock(return_value=mock_config))
    def test_decode_error(self, mock_token, mock_handler):
        with pytest.raises(JWTDecodeError):
            with patch.object(jwt, "decode", side_effect=JWTError):
                mock_handler.decode(mock_token)

    @patch("core.security.jwt.config", MagicMock(return_value=mock_config))
    def test_decode_expired(self, mock_expired_token, mock_handler):
        decoded = mock_handler.decode_expired(mock_expired_token)
        assert decoded is not None
        assert isinstance(decoded, dict)

    @patch("core.security.jwt.config", MagicMock(return_value=mock_config))
    def test_decode_error(self, mock_token, mock_handler):
        with pytest.raises(JWTDecodeError):
            with patch.object(jwt, "decode", side_effect=JWTError):
                mock_handler.decode(mock_token)

    @patch("core.security.jwt.config", MagicMock(return_value=mock_config))
    def test_decode_expired_error(self, mock_handler):
        with pytest.raises(JWTDecodeError):
            with patch.object(jwt, "decode", side_effect=JWTError):
                mock_handler.decode_expired(mock_token)
