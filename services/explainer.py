import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

def explain_similarity(book_a: dict, book_b: dict) -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""You are a literary analyst. A user liked "{book_a['title']}" and I recommended "{book_b['title']}".

    Book A - {book_a['title']} by {', '.join(book_a['authors'])}:
    {book_a['description']}

    Book B - {book_b['title']} by {', '.join(book_b['authors'])}:
    {book_b['description']}

    Respond with a JSON object in this exact structure, no other text:                                  
    {{
      "similar": ["point 1", "point 2", "point 3"],                                                   
      "different": ["point 1", "point 2", "point 3"],
      "recommended_because": "one sentence explanation"
    }}
    """

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    return json.loads(message.content[0].text)
