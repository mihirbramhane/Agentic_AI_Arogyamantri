// app/api/analyze/route.ts
// Proxies the browser request to the CrewAI FastAPI backend so the backend URL
// and any server-only concerns stay off the client. Auth is enforced with your
// existing Supabase session before the crew runs.

import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

const BACKEND_URL = process.env.AGENT_BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  // --- 1. Require an authenticated user (reuses your SkillProof Supabase auth) ---
  const cookieStore = cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get: (name: string) => cookieStore.get(name)?.value,
      },
    }
  );
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  // --- 2. Forward the multipart form (profile JSON + optional bill file) ---
  const incoming = await req.formData();
  const forward = new FormData();
  const profile = incoming.get("profile");
  const bill = incoming.get("bill");
  if (profile) forward.append("profile", profile as string);
  if (bill && bill instanceof File) forward.append("bill", bill);

  const resp = await fetch(`${BACKEND_URL}/analyze`, {
    method: "POST",
    body: forward,
  });

  if (!resp.ok) {
    return NextResponse.json(
      { error: `Backend error (${resp.status})` },
      { status: 502 }
    );
  }
  const data = await resp.json();
  return NextResponse.json(data);
}
