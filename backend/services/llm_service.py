from openai import OpenAI
from backend.core.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_BASE_URL,
    DEEPSEEK_MODEL,
)


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
        blocks.append(
            f"[Document {i}]\n"
            f"Source: {item['title']}\n"
            f"Content: {item['snippet']}"
        )
    return "\n\n".join(blocks)


def generate_answer(query: str, retrieved_sources: list[dict]) -> str:
    if not retrieved_sources:
        return "Could not find relevant information in the indexed documents."

    context = build_context(retrieved_sources)

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
            max_tokens=300,
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