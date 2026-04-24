import anthropic
import instructor
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = instructor.from_anthropic(
    anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
)


class BookExplanation(BaseModel):
    similar: list[str]
    different: list[str]
    recommended_because: str


def explain_similarity(book_a: dict, book_b: dict) -> dict:
    prompt = f"""You are a literary analyst. A user liked "{book_a['title']}" and I recommended "{book_b['title']}".

    Book A - {book_a['title']} by {', '.join(book_a['authors'])}:
    {book_a['description']}

    Book B - {book_b['title']} by {', '.join(book_b['authors'])}:
    {book_b['description']}

    Explain what makes these books similar and different
    """

    explanation = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
        response_model=BookExplanation,
    )

    return explanation.model_dump()
