import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = (
  process.env.BACKEND_INTERNAL_URL ||
  process.env.BACKEND_URL ||
  "https://tinvix-1.onrender.com"
).replace(/\/$/, "");

export async function GET(req: NextRequest, { params }: { params: { path: string[] } }) {
  return proxyRequest(req, params.path);
}

export async function POST(req: NextRequest, { params }: { params: { path: string[] } }) {
  return proxyRequest(req, params.path);
}

async function proxyRequest(req: NextRequest, pathSegments: string[]) {
  const path = (pathSegments || []).join("/");
  const url = new URL(req.url);
  const targetUrl = `${BACKEND_URL}/api/${path}${url.search}`;

  const headers = new Headers(req.headers);
  headers.delete("host");
  headers.delete("connection");

  const isBodyAllowed = req.method !== "GET" && req.method !== "HEAD";
  const body = isBodyAllowed ? await req.blob() : undefined;

  let lastError: any = null;
  // Retry loop up to 3 times to smoothly handle cold starts on Render free tier
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const res = await fetch(targetUrl, {
        method: req.method,
        headers,
        body,
        cache: "no-store",
        signal: AbortSignal.timeout(35000),
      });

      const resBody = await res.arrayBuffer();
      return new NextResponse(resBody, {
        status: res.status,
        headers: {
          "content-type": res.headers.get("content-type") || "application/json",
        },
      });
    } catch (err: any) {
      lastError = err;
      if (attempt < 2) {
        await new Promise((r) => setTimeout(r, 2000));
      }
    }
  }

  return NextResponse.json(
    { error: "Backend proxy error", details: lastError?.message, target: targetUrl },
    { status: 502 }
  );
}
