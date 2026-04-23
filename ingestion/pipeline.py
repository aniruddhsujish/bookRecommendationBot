import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from ingestion.google_books_client import fetch_books, Book, QuotaExceededException

load_dotenv()

SUBJECTS = [
    # Fiction genres
    "science fiction",
    "fantasy",
    "mystery",
    "thriller",
    "romance",
    "historical fiction",
    "horror",
    "literary fiction",
    "crime",
    "adventure",
    "young adult",
    "classic literature",
    "dystopian",
    "space opera",
    "cyberpunk",
    "urban fantasy",
    "paranormal",
    "detective fiction",
    "psychological thriller",
    "magical realism",
    "steampunk",
    "epic fantasy",
    "dark fantasy",
    "spy fiction",
    "western fiction",
    "gothic fiction",
    "satire",
    "short stories",
    "mythology",
    # Non-fiction
    "biography",
    "autobiography",
    "memoir",
    "self help",
    "philosophy",
    "psychology",
    "science",
    "history",
    "politics",
    "economics",
    "business",
    "finance",
    "technology",
    "medicine",
    "true crime",
    "travel writing",
    "nature writing",
    "food writing",
    "sports",
    "religion",
    "spirituality",
    "art history",
    "music",
    "film",
    "anthropology",
    "sociology",
    "education",
    "parenting",
    "health",
    "environment",
    "astronomy",
    "mathematics",
    "physics",
    "evolution",
    # By era/region
    "ancient history",
    "world war",
    "american history",
    "british literature",
    "african literature",
    "asian literature",
    "latin american literature",
    "russian literature",
    "french literature",
    "contemporary fiction",
    # More specific fiction subgenres
    "space opera",
    "cyberpunk",
    "dystopian fiction",
    "post apocalyptic",
    "alternate history",
    "time travel",
    "hard science fiction",
    "soft science fiction",
    "military science fiction",
    "first contact",
    "artificial intelligence fiction",
    "vampire fiction",
    "werewolf fiction",
    "zombie fiction",
    "supernatural fiction",
    "cozy mystery",
    "police procedural",
    "legal thriller",
    "medical thriller",
    "financial thriller",
    "espionage thriller",
    "heist fiction",
    "noir fiction",
    "sword and sorcery",
    "dark fantasy",
    "portal fantasy",
    "fairy tale retelling",
    "romantic suspense",
    "historical romance",
    "contemporary romance",
    "paranormal romance",
    # Non-fiction subgenres
    "narrative nonfiction",
    "popular science",
    "popular psychology",
    "behavioral economics",
    "neuroscience",
    "evolutionary biology",
    "climate change",
    "artificial intelligence",
    "cryptocurrency",
    "startups",
    "leadership",
    "productivity",
    "habit formation",
    "mindfulness",
    "stoicism",
    "eastern philosophy",
    "political philosophy",
    "american politics",
    "foreign policy",
    "social justice",
    "feminism",
    "world war 2",
    "cold war",
    "ancient rome",
    "ancient greece",
    "medieval history",
    "renaissance",
    "industrial revolution",
    "civil rights",
    "colonialism",
    # By audience and format
    "coming of age",
    "bildungsroman",
    "campus novel",
    "domestic fiction",
    "family saga",
    "multigenerational fiction",
    "immigrant fiction",
    "short story collection",
    "essay collection",
    "narrative journalism",
    "investigative journalism",
    "long form journalism",
    # Award and list based
    "hugo award",
    "nebula award",
    "booker prize",
    "pulitzer prize fiction",
    "national book award",
    "oprah book club",
    "reese book club",
]

MAX_PAGES_PER_SUBJECT = 25
RATE_LIMIT_DELAY = 2.5
CHECKPOINT_FILE = "checkpoint.json"


def load_checkpoint() -> dict:
    if Path(CHECKPOINT_FILE).exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"completed_subjects": [], "seen_ids": []}


def save_checkpoint(checkpoint: dict):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f)


def save_books(books: list[Book], path: str = "books.json"):
    with open(path, "w") as f:
        json.dump([b.__dict__ for b in books], f, indent=2)
    print(f"Saved {len(books)} books to {path}")


def load_books(path: str = "books.json") -> list[Book]:
    if not Path(path).exists():
        return []
    with open(path) as f:
        data = json.load(f)
    return [Book(**b) for b in data]


def append_books(new_books: list[Book], path: str = "books.json"):
    existing = load_books(path)
    all_books = existing + new_books
    with open(path, "w") as f:
        json.dump([b.__dict__ for b in all_books], f)
    print(f" Saved {len(new_books)} books:({len(all_books)} total in file)")


async def run_pipeline() -> list[Book]:
    api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    checkpoint = load_checkpoint()

    MAX_DAILY_REQUESTS = 950
    requests_made = 0
    completed_subjects = set(checkpoint["completed_subjects"])
    existing_books = load_books()
    seen_ids = set(checkpoint["seen_ids"])
    seen_ids.update(b.id for b in existing_books)
    all_books: list[Book] = []

    for subject in SUBJECTS:
        if subject in completed_subjects:
            print(f"Skipping '{subject}' - Already done")
            continue

        print(f"Fetching '{subject}'...")
        subject_books: list[Book] = []

        for page in range(MAX_PAGES_PER_SUBJECT):
            start_index = page * 40
            try:
                books, raw_count = await fetch_books(
                    query=subject, api_key=api_key, start_index=start_index
                )
            except QuotaExceededException:
                print("Daily quota exceeded. Saving checkpoint and exiting.")
                save_checkpoint(
                    {
                        "completed_subjects": list(completed_subjects),
                        "seen_ids": list(seen_ids),
                    }
                )
                return all_books
            except Exception as e:
                print(f" Skipping page {page+1} due to error: {e}")
                break
            new_books = [b for b in books if b.id not in seen_ids]
            seen_ids.update(b.id for b in new_books)
            subject_books.extend(new_books)

            print(f" Page {page + 1}: {len(new_books)} new books")
            await asyncio.sleep(RATE_LIMIT_DELAY)

            # Checking if daily limit is met. Else it could just continuosly fail with 429 error
            requests_made += 1
            if requests_made >= MAX_DAILY_REQUESTS:
                print(f"Approaching daily quota limit. Stopping for today.")
                save_checkpoint(
                    {
                        "completed_subjects": list(completed_subjects),
                        "seen_ids": list(seen_ids),
                    }
                )
                return all_books

            # TODO: edge case - if all books on a page are filtered out but Google
            # has more pages, we exit early. Fix: use raw_count from fetch_books.
            if raw_count == 0:
                print(f" Early exit - Google returned zero results")
                break

        all_books.extend(subject_books)
        completed_subjects.add(subject)
        append_books(subject_books)
        save_checkpoint(
            {"completed_subjects": list(completed_subjects), "seen_ids": list(seen_ids)}
        )
        print(f" Total unique books so far: {len(seen_ids)}")

    print(f"\nPipeline complete. Total books: {len(all_books)}")
    return all_books
