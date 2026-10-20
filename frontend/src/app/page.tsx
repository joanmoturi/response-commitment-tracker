"use client";

import { useState } from "react";
import { AuthForm } from "@/features/auth/auth-form";
import { useAuth } from "@/features/auth/auth-provider";
import { ErrorMessage } from "@/components/error-message";
import { RequestWorkspace } from "@/features/requests/request-workspace";

export default function Home() {
  const { user, loading, error, logout } = useAuth();
  const [logoutError, setLogoutError] = useState<string | null>(null);
  const [loggingOut, setLoggingOut] = useState(false);

  async function signOut() {
    setLoggingOut(true);
    setLogoutError(null);
    try {
      await logout();
    } catch (cause: unknown) {
      setLogoutError(cause instanceof Error ? cause.message : "Sign out failed.");
    } finally {
      setLoggingOut(false);
    }
  }

  return <main className="mx-auto max-w-5xl space-y-6 px-4 py-10 sm:py-12">
    <header className="flex flex-wrap items-center justify-between gap-4">
      <div>
        <p className="text-sm font-medium uppercase tracking-widest text-sky-300">Response tracking</p>
        <h1 className="mt-2 text-3xl font-bold sm:text-4xl">Keep every commitment visible.</h1>
        <p className="mt-2 max-w-2xl text-slate-400">Capture what response is needed, who owns it, and when it is due.</p>
      </div>
      {user && <div className="space-y-2"><p className="text-sm">{user.email}</p><button className="button" disabled={loggingOut} onClick={signOut}>Sign out</button></div>}
    </header>
    <ErrorMessage message={logoutError ?? error} />
    {loading ? <p role="status">Restoring session...</p> : user ? <RequestWorkspace key={user.id} /> : <AuthForm />}
  </main>;
}
