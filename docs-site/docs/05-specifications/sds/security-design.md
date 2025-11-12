---
id: sds-security-design
title: SDS - Security Design
description: Software design specification - security design
sidebar_label: Security Design
sidebar_position: 7
tags:
  - specification
  - design
  - architecture
---

:::info Navigation
- [Introduction](introduction.md)
- [System Architecture](system-architecture.md)
- [Component Design](component-design.md)
- [Database Design](database-design.md)
- [API Design](api-design.md)
- [Data Pipeline](data-pipeline.md)
- [Security Design](security-design.md) (Current)
- [Performance Design](performance-design.md)
- [Deployment](deployment.md)
- [Tech Stack & Decisions](tech-stack-decisions.md)
:::

# Software Design Specification - Security Design

## 7. Security Design

### 7.1 Authentication & Authorization

#### 7.1.1 JWT Token Design

**Token Structure**:

```json
// Access Token (15 minutes)
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "email": "user@example.com",
    "tier": "pro",
    "iat": 1699456789,
    "exp": 1699457689
  },
  "signature": "..."
}

// Refresh Token (30 days)
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "type": "refresh",
    "iat": 1699456789,
    "exp": 1701048789
  },
  "signature": "..."
}
```

**Implementation**:

```python
# core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire
    }
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def decode_access_token(token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
```

#### 7.1.2 OAuth Integration

**Supported Providers**: Kakao, Naver, Google

```python
# services/oauth_service.py
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()

# Kakao
oauth.register(
    name='kakao',
    client_id=settings.KAKAO_CLIENT_ID,
    client_secret=settings.KAKAO_CLIENT_SECRET,
    access_token_url='https://kauth.kakao.com/oauth/token',
    authorize_url='https://kauth.kakao.com/oauth/authorize',
    api_base_url='https://kapi.kakao.com',
    client_kwargs={'scope': 'profile_nickname profile_image account_email'}
)

# Naver
oauth.register(
    name='naver',
    client_id=settings.NAVER_CLIENT_ID,
    client_secret=settings.NAVER_CLIENT_SECRET,
    access_token_url='https://nid.naver.com/oauth2.0/token',
    authorize_url='https://nid.naver.com/oauth2.0/authorize',
    api_base_url='https://openapi.naver.com',
    client_kwargs={'scope': 'profile'}
)

# Google
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url=(
        'https://accounts.google.com/.well-known/openid-configuration'
    ),
    client_kwargs={'scope': 'openid email profile'}
)
```

### 7.2 Data Security

#### 7.2.1 Data Encryption

**In Transit**:
- TLS 1.3 for all HTTPS connections
- Certificate management (Let's Encrypt)

**At Rest**:
- PostgreSQL column encryption for PII
- Environment variable encryption (Vault/AWS Secrets Manager)

```python
# core/encryption.py
from cryptography.fernet import Fernet
from app.core.config import settings

cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_value(value: str) -> str:
    """Encrypt sensitive data."""
    return cipher_suite.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    """Decrypt sensitive data."""
    return cipher_suite.decrypt(encrypted_value.encode()).decode()
```

**Database Model with Encryption**:

```python
# db/models/user.py
from sqlalchemy import Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.encryption import encrypt_value, decrypt_value

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    _phone_number = Column("phone_number", String)  # Encrypted

    @hybrid_property
    def phone_number(self):
        """Decrypt phone number."""
        if self._phone_number:
            return decrypt_value(self._phone_number)
        return None

    @phone_number.setter
    def phone_number(self, value: str):
        """Encrypt phone number."""
        if value:
            self._phone_number = encrypt_value(value)
        else:
            self._phone_number = None
```

### 7.3 Input Validation

#### 7.3.1 Pydantic Schemas

```python
# schemas/screening.py
from pydantic import BaseModel, validator, Field
from typing import Optional, Dict
from enum import Enum

class Market(str, Enum):
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    ALL = "ALL"

class FilterRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None

    @validator('min', 'max')
    def check_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v

class ScreeningRequest(BaseModel):
    market: Market = Market.ALL
    filters: Dict[str, FilterRange] = Field(default_factory=dict)
    sort_by: str = "market_cap"
    order: str = Field("desc", regex="^(asc|desc)$")
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=100)

    @validator('filters')
    def validate_filters(cls, v):
        """Validate filter keys are allowed indicators."""
        allowed_filters = {
            'per', 'pbr', 'psr', 'roe', 'roa',
            'operating_margin', 'net_margin',
            'revenue_growth_yoy', 'profit_growth_yoy',
            'debt_to_equity', 'current_ratio',
            'dividend_yield', 'market_cap',
            'quality_score', 'value_score', 'growth_score'
        }

        invalid_keys = set(v.keys()) - allowed_filters
        if invalid_keys:
            raise ValueError(f"Invalid filters: {invalid_keys}")

        return v
```

### 7.4 SQL Injection Prevention

**Using SQLAlchemy ORM** (Parameterized Queries):

```python
# ✅ SAFE: Using ORM
stocks = db.query(Stock).filter(Stock.market == market).all()

# ✅ SAFE: Using parameterized raw SQL
stocks = db.execute(
    "SELECT * FROM stocks WHERE market = :market",
    {"market": market}
).fetchall()

# ❌ UNSAFE: String concatenation (NEVER DO THIS)
stocks = db.execute(
    f"SELECT * FROM stocks WHERE market = '{market}'"
).fetchall()
```

### 7.5 CORS Configuration

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://screener.kr",
        "https://www.screener.kr",
        "http://localhost:5173",  # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

### 7.6 Content Security Policy

```python
# middleware/security.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.screener.kr;"
    )

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    return response
```

---