import json
from openai import OpenAI
from backend.core.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_BASE_URL,
    DEEPSEEK_MODEL,
)

VALID_ROUTES = {"faq", "mandai", "hybrid", "verify_web"}

CLASSIFY_SYSTEM_PROMPT = """You are a routing classifier for a RAG chatbot.

Your job is to classify the user's query into exactly one route:
- faq: general visitor questions like tickets, hours, access, facilities, policies
- mandai: questions about animals, shows, park attractions, species facts, or park-specific content
- hybrid: questions requiring multiple internal sources
- verify_web: questions asking for latest information, official confirmation, or external validation

Return only valid JSON:
{"route": "<faq|mandai|hybrid|verify_web>", "reason": "<short reason>"}
"""

def get_client():
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("No API key set. Set DEEPSEEK_API_KEY.")

    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_API_BASE_URL,
    )


def build_context(retrieved_sources: list[dict]) -> str:
    if not retrieved_sources:
        return "No relevant context retrieved."

    blocks = []
    for i, item in enumerate(retrieved_sources, start=1):
        content = item.get("full_text") or item.get("snippet") or ""
        blocks.append(
            f"[Document {i}]\n"
            f"Source: {item.get('title', 'Unknown source')}\n"
            f"Content:\n{content}"
        )
    return "\n\n".join(blocks)


def classify_route(query: str) -> dict:
    """
    Use the LLM to classify an ambiguous or uncertain query into a route.
    """
    client = get_client()

    user_prompt = f"User query: {query}"

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=200
        )

        raw_text = response.choices[0].message.content.strip()
        print("CLASSIFIER RAW OUTPUT:", raw_text)
        parsed = json.loads(raw_text)

        route = parsed.get("route")
        reason = parsed.get("reason", "No reason provided").strip()

        if route not in VALID_ROUTES:
            raise ValueError(f"Invalid route: {route!r}")

        return {"route": route, "reason": reason}
    except Exception:
        return {"route": "hybrid", "reason": "LLM output invalid, defaulted to hybrid"}


def generate_answer(query: str, retrieved_sources: list[dict]) -> str:
    if not retrieved_sources:
        return "Could not find relevant information in the indexed documents."

    context = build_context(retrieved_sources)
    print(context[:3000])

    system_prompt = (
        "You are a helpful assistant for Mandai Wildlife Reserve. "
        "Answer only using the retrieved context. "
        "If the answer is not contained in the context, say that clearly. "
        "Keep the answer concise, direct, and natural. "
        "Do not dump the raw context back to the user."
    )

    user_prompt = f"""
Retrieved context:
{context}

User question:
{query}
"""

    client = get_client()

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=700,
        )

        try:
            return response.choices[0].message.content.strip()
        except Exception:
            return "The assistant could not produce a valid response."

    except Exception:
        try:
            top_source = retrieved_sources[0]
            return (
                f"I found relevant information in {top_source['title']}, "
                f"but the LLM request failed. Top snippet: {top_source['snippet']}"
            )
        except Exception:
            return "The external LLM request failed; cannot generate an answer right now."
        
def generate_web_verified_answer(query: str, web_sources: list[dict]) -> str:
    if not web_sources:
        return "I could not find enough reliable web information to verify this."

    context = build_context(web_sources)
    print(context[:3000])

    system_prompt = (
        "You are a careful assistant performing external web verification. "
        "Use only the provided web evidence. "
        "Answer the user's question clearly and directly. "
        "If the evidence is insufficient, say that clearly. "
        "Do not invent facts beyond the provided web evidence."
    )

    user_prompt = f"""
Web evidence:
{context}

User question:
{query}
"""

    client = get_client()

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=700,
        )

        return response.choices[0].message.content.strip()

    except Exception:
        try:
            top_source = web_sources[0]
            return (
                f"I found web information in {top_source['title']}, "
                f"but the verification summary failed. Top snippet: {top_source['snippet']}"
            )
        except Exception:
            return "The external web verification request failed."