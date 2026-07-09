import os
from openai import OpenAI

def get_model_name():
    return os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

def get_client():
    api_key = os.getenv("DEEPSEEK_API_KEY") 
    base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise RuntimeError("No API key set. Set DEEPSEEK_API_KEY.")
    
    return OpenAI(api_key=api_key, base_url=base_url)

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
    model_name = get_model_name()
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=300,
        )

        # Safely extract the assistant content
        try:
            return response.choices[0].message.content.strip()
        except Exception:
            # unexpected response shape
            return "The assistant could not produce a valid response."
    except Exception as e:
        # API call failed: fallback to simple rule-based answer using context
        # Keep concise: try to find a sentence from context that mentions the query keywords
        try:
            q_words = [w.lower() for w in query.split() if len(w) > 3]
            context = context.lower()
            for sent in context.split('\n'):
                s = sent.lower()
                if all(w in s for w in q_words[:3]):
                    return sent.strip()
        except Exception:
            pass
        return "The external LLM request failed; cannot generate an answer right now."