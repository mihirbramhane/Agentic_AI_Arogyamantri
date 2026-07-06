// lib/aarogyamitra.ts
// Client-side helper: submit the profile + bill to /api/analyze, then speak the
// guidance aloud using the Web Speech API (reuses your SkillProof voice work).

export interface UserProfile {
  state: string;
  annual_income: number;
  family_size: number;
  has_ration_card: boolean;
  ration_card_type?: string;
  existing_insurance?: string;
  ailment?: string;
  language: string; // "en" | "hi" | "te" | "ta" | ...
  latitude?: number;
  longitude?: number;
}

export interface AnalyzeResult {
  voice_guidance: string;
  raw_report?: string;
  disclaimer?: string;
  error?: string;
}

export async function analyze(
  profile: UserProfile,
  bill?: File
): Promise<AnalyzeResult> {
  const form = new FormData();
  form.append("profile", JSON.stringify(profile));
  if (bill) form.append("bill", bill);

  const res = await fetch("/api/analyze", { method: "POST", body: form });
  return (await res.json()) as AnalyzeResult;
}

const LANG_TAGS: Record<string, string> = {
  en: "en-IN",
  hi: "hi-IN",
  te: "te-IN",
  ta: "ta-IN",
  bn: "bn-IN",
  mr: "mr-IN",
};

/** Speak the guidance aloud in the user's language. */
export function speak(text: string, language = "en") {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = LANG_TAGS[language] ?? "en-IN";
  utter.rate = 0.95;
  window.speechSynthesis.speak(utter);
}

export function stopSpeaking() {
  if (typeof window !== "undefined" && "speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
}
