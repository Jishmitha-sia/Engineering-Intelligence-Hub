"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface OAuthProviders {
  google: boolean;
  github: boolean;
}

export function OAuthButtons() {
  const [providers, setProviders] = useState<OAuthProviders>({
    google: false,
    github: false,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadProviders = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/oauth/providers`);
        if (response.ok) {
          setProviders((await response.json()) as OAuthProviders);
        }
      } finally {
        setIsLoading(false);
      }
    };

    void loadProviders();
  }, []);

  if (isLoading) {
    return null;
  }

  if (!providers.google && !providers.github) {
    return (
      <p className="text-center text-xs text-slate-500">
        Social login is available when Google/GitHub OAuth credentials are set in
        `.env`.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {providers.google ? (
        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => {
            window.location.href = `${API_BASE_URL}/api/v1/auth/google/login`;
          }}
        >
          Continue with Google
        </Button>
      ) : null}
      {providers.github ? (
        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => {
            window.location.href = `${API_BASE_URL}/api/v1/auth/github/login`;
          }}
        >
          Continue with GitHub
        </Button>
      ) : null}
    </div>
  );
}
