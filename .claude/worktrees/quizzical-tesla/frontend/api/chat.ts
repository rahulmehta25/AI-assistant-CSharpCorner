import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

export const config = {
  runtime: "edge",
};

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface UserProfile {
  name?: string;
  title?: string;
  experience?: string;
  education?: string;
  location?: string;
  interests?: string[];
  skills?: { name: string; level: string; category: string }[];
}

export default async function handler(req: Request) {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return new Response(
      JSON.stringify({ error: "API key not configured" }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  let body: { messages: ChatMessage[]; userProfile?: UserProfile };
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid request body" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const { messages, userProfile } = body;

  if (!messages || !Array.isArray(messages) || messages.length === 0) {
    return new Response(JSON.stringify({ error: "Messages are required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const profileContext = userProfile
    ? `
The user's profile:
- Name: ${userProfile.name || "Not specified"}
- Current title: ${userProfile.title || "Not specified"}
- Experience level: ${userProfile.experience || "Not specified"}
- Education: ${userProfile.education || "Not specified"}
- Location: ${userProfile.location || "Not specified"}
- Interests: ${userProfile.interests?.join(", ") || "Not specified"}
- Skills: ${userProfile.skills?.map((s) => `${s.name} (${s.level})`).join(", ") || "Not specified"}
`
    : "";

  const systemPrompt = `You are an expert AI career counselor with deep knowledge of the job market, career paths, skill development, and professional growth. You provide personalized, actionable career guidance.

${profileContext}

Your role is to:
1. Provide specific, actionable career advice tailored to the user's background and goals
2. Suggest realistic career paths with clear progression steps
3. Identify skill gaps and recommend concrete learning resources
4. Give honest assessments of job market conditions and salaries
5. Help with job search strategies, resume tips, and interview preparation
6. Be encouraging but realistic — set accurate expectations

Format your responses with:
- Clear sections using **bold headers** when covering multiple topics
- Bullet points for lists of recommendations
- Specific tool, course, or resource names (not generic suggestions)
- Concrete next steps the user can take this week

Keep responses focused and actionable. Avoid generic advice. Reference the user's specific skills and background when relevant.`;

  try {
    const response = await client.messages.create({
      model: "claude-opus-4-6",
      max_tokens: 1024,
      system: systemPrompt,
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    });

    const content = response.content[0];
    if (content.type !== "text") {
      throw new Error("Unexpected response type");
    }

    return new Response(JSON.stringify({ response: content.text }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    console.error("Claude API error:", error);
    const message =
      error instanceof Error ? error.message : "Failed to get AI response";
    return new Response(JSON.stringify({ error: message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
