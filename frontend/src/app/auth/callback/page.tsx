"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiRequest } from "@/lib/api";
import { User, setStoredToken } from "@/lib/auth";
import { useAuth } from "@/contexts/AuthContext";

function OAuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { applyAuthResponse } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const completeLogin = async () => {
      const accessToken = searchParams.get("access_token");
      if (!accessToken) {
        setError("Missing access token from OAuth provider.");
        return;
      }

      try {
        setStoredToken(accessToken);
        const user = await apiRequest<User>(
          "/api/v1/auth/me",
          { method: "GET" },
          accessToken,
        );
        applyAuthResponse({
          success: true,
          message: "OAuth login successful",
          data: {
            access_token: accessToken,
            token_type: "bearer",
            expires_in: 0,
            user,
          },
        });
        router.replace("/dashboard");
      } catch {
        setError("Unable to complete social sign-in. Please try again.");
      }
    };

    void completeLogin();
  }, [applyAuthResponse, router, searchParams]);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
      {error ? (
        <>
          <p className="text-red-600">{error}</p>
          <button
            type="button"
            className="mt-4 text-sm font-medium text-slate-900 underline"
            onClick={() => router.replace("/login")}
          >
            Back to sign in
          </button>
        </>
      ) : (
        <p className="text-slate-600">Completing sign-in...</p>
      )}
    </div>
  );
}

export default function OAuthCallbackPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <Suspense fallback={<p className="text-slate-600">Completing sign-in...</p>}>
        <OAuthCallbackContent />
      </Suspense>
    </div>
  );
}
