"""
OAuth login helpers for Google and GitHub.
"""

import secrets
from datetime import timedelta
from typing import Any, Optional
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from core.security import create_access_token, hash_password
from models.user import User
from schemas.user import TokenResponse, UserResponse

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"


class OAuthService:
    """Google and GitHub OAuth flows."""

    def is_google_enabled(self) -> bool:
        return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    def is_github_enabled(self) -> bool:
        return bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET)

    def _create_state(self, provider: str) -> str:
        return create_access_token(
            subject=f"oauth:{provider}",
            expires_delta=timedelta(minutes=10),
        )

    def _verify_state(self, provider: str, state: str) -> None:
        from core.security import verify_token

        payload = verify_token(state)
        if not payload or payload.get("sub") != f"oauth:{provider}":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth state",
            )

    def get_google_login_url(self) -> str:
        if not self.is_google_enabled():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google sign-in is not configured",
            )

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": f"{settings.OAUTH_BACKEND_BASE_URL}/api/v1/auth/google/callback",
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "select_account",
            "state": self._create_state("google"),
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    def get_github_login_url(self) -> str:
        if not self.is_github_enabled():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GitHub sign-in is not configured",
            )

        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": f"{settings.OAUTH_BACKEND_BASE_URL}/api/v1/auth/github/callback",
            "scope": "read:user user:email",
            "state": self._create_state("github"),
        }
        return f"{GITHUB_AUTH_URL}?{urlencode(params)}"

    async def _upsert_oauth_user(
        self,
        db: AsyncSession,
        provider: str,
        subject: str,
        email: str,
        full_name: Optional[str],
    ) -> User:
        result = await db.execute(
            select(User).where(
                or_(
                    and_(
                        User.oauth_provider == provider,
                        User.oauth_subject == subject,
                    ),
                    User.email == email.lower(),
                )
            )
        )
        user = result.scalar_one_or_none()

        if user:
            user.email = email.lower()
            if full_name and not user.full_name:
                user.full_name = full_name
            if not user.oauth_provider:
                user.oauth_provider = provider
                user.oauth_subject = subject
            await db.commit()
            await db.refresh(user)
            return user

        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            is_active=True,
            is_verified=True,
            oauth_provider=provider,
            oauth_subject=subject,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    def _build_login_redirect(self, access_token: str) -> str:
        params = urlencode(
            {
                "access_token": access_token,
                "token_type": "bearer",
            }
        )
        return f"{settings.OAUTH_FRONTEND_CALLBACK_URL}?{params}"

    async def handle_google_callback(
        self,
        db: AsyncSession,
        code: str,
        state: str,
    ) -> str:
        self._verify_state("google", state)

        async with httpx.AsyncClient(timeout=20.0) as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": f"{settings.OAUTH_BACKEND_BASE_URL}/api/v1/auth/google/callback",
                    "grant_type": "authorization_code",
                },
            )
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange Google authorization code",
                )
            token_data = token_response.json()
            user_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch Google profile",
            )

        profile: dict[str, Any] = user_response.json()
        email = profile.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google account did not return an email address",
            )

        user = await self._upsert_oauth_user(
            db,
            provider="google",
            subject=str(profile.get("sub")),
            email=email,
            full_name=profile.get("name"),
        )
        access_token = create_access_token(subject=user.id)
        return self._build_login_redirect(access_token)

    async def handle_github_callback(
        self,
        db: AsyncSession,
        code: str,
        state: str,
    ) -> str:
        self._verify_state("github", state)

        async with httpx.AsyncClient(timeout=20.0) as client:
            token_response = await client.post(
                GITHUB_TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "code": code,
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "redirect_uri": f"{settings.OAUTH_BACKEND_BASE_URL}/api/v1/auth/github/callback",
                },
            )
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange GitHub authorization code",
                )
            token_data = token_response.json()
            access = token_data.get("access_token")
            if not access:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="GitHub did not return an access token",
                )

            headers = {
                "Authorization": f"Bearer {access}",
                "Accept": "application/vnd.github+json",
            }
            user_response = await client.get(GITHUB_USER_URL, headers=headers)
            emails_response = await client.get(GITHUB_EMAILS_URL, headers=headers)

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch GitHub profile",
            )

        profile: dict[str, Any] = user_response.json()
        email = profile.get("email")
        if not email and emails_response.status_code == 200:
            for item in emails_response.json():
                if item.get("primary") and item.get("verified"):
                    email = item.get("email")
                    break
            if not email:
                for item in emails_response.json():
                    if item.get("verified"):
                        email = item.get("email")
                        break

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub account did not return a verified email address",
            )

        user = await self._upsert_oauth_user(
            db,
            provider="github",
            subject=str(profile.get("id")),
            email=email,
            full_name=profile.get("name") or profile.get("login"),
        )
        access_token = create_access_token(subject=user.id)
        return self._build_login_redirect(access_token)

    async def build_token_response(self, db: AsyncSession, user: User) -> TokenResponse:
        access_token = create_access_token(subject=user.id)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )
