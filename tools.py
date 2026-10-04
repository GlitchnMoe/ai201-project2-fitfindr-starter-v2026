"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings
import re


#Helper functions
def _words(text: str) -> set[str]:
    """Turn text into lowercase words for keyword matching."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _size_matches(requested_size: str, listing_size: str) -> bool:
    """
    Match a requested size without accidental substring matches.

    Examples:
        M matches M and S/M
        S does not match US 9
        L does not match XL
    """
    requested = requested_size.strip().lower()
    actual = listing_size.strip().lower()

    if requested == actual:
        return True

    pattern = rf"(?<![a-z0-9]){re.escape(requested)}(?![a-z0-9])"
    return re.search(pattern, actual) is not None


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    listings = load_listings()

    # Common words that should not influence clothing relevance.
    ignored_words = {
        "a", "an", "the", "for", "i", "im", "i'm",
        "looking", "want", "need", "find", "me",
        "some", "something", "under", "size",
    }

    description_words = _words(description) - ignored_words

    scored_results = []

    for listing in listings:
        # Price filter.
        if max_price is not None and listing["price"] > max_price:
            continue

        # Size filter.
        if size is not None and not _size_matches(size, listing["size"]):
            continue

        # Search the fields that describe what the item is/style it has.
        searchable_text = " ".join([
            listing["title"],
            listing["description"],
            listing["category"],
            " ".join(listing["style_tags"]),
        ])

        listing_words = _words(searchable_text)

        # One point for each requested keyword found.
        score = len(description_words & listing_words)

        # A zero-score listing is not a description match.
        if score == 0:
            continue

        scored_results.append((score, listing))

    # Best keyword match first.
    # For equal scores, prefer the cheaper listing as stated in our spec.
    scored_results.sort(
        key=lambda result: (-result[0], result[1]["price"])
    )

    return [
        listing
        for _, listing in scored_results[:config.SEARCH_RESULT_LIMIT]
    ]

# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    wardrobe_items = wardrobe.get("items", [])

    item_details = (
        f"Item: {new_item['title']}\n"
        f"Description: {new_item['description']}\n"
        f"Category: {new_item['category']}\n"
        f"Colors: {', '.join(new_item['colors'])}\n"
        f"Style tags: {', '.join(new_item['style_tags'])}\n"
    )

    if not wardrobe_items:
        prompt = f"""
{item_details}

The user's wardrobe is empty.

Suggest exactly two different outfits built around this item using general
clothing and footwear recommendations. Be specific enough that the user knows
what pieces, colors, and styling choices would work.
""".strip()

        response = generate(
            prompt,
            system=(
                "You are a clothing stylist. Give practical, concise outfit "
                "suggestions based on the item provided."
            ),
        )

        return response or (
            "Try styling this item with simple neutral basics and shoes that "
            "match its overall style."
        )

    wardrobe_lines = []

    for item in wardrobe_items:
        name = item.get("name", "Unnamed item")

        details = ", ".join(
            f"{key}: {value}"
            for key, value in item.items()
            if key != "name"
        )

        if details:
            wardrobe_lines.append(f"- {name} ({details})")
        else:
            wardrobe_lines.append(f"- {name}")

    wardrobe_text = "\n".join(wardrobe_lines)

    prompt = f"""
{item_details}

The user already owns these wardrobe pieces:

{wardrobe_text}

Create exactly two outfit suggestions built around the new item.

Use pieces from the wardrobe whenever they fit the outfit. When you use a
wardrobe piece, write its name exactly as it appears above. Do not pretend the
user owns pieces that are not listed. Briefly explain why each combination
works.
""".strip()

    response = generate(
        prompt,
        system=(
            "You are a clothing stylist helping someone style a second-hand "
            "purchase using clothes they already own."
        ),
    )

    return response or (
        "I couldn't generate the outfit suggestions, but the selected item "
        "can be paired with complementary basics from the wardrobe."
    )

# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return (
            "A fit card could not be created because no outfit suggestion "
            "was provided."
        )

    price = new_item["price"]

    if isinstance(price, (int, float)):
        price_text = f"${price:g}"
    else:
        price_text = f"${price}"

    prompt = f"""
Write a social-media-style caption about this second-hand find.

Item: {new_item['title']}
Description: {new_item['description']}
Price: {price_text}
Platform: {new_item['platform']}
Style tags: {', '.join(new_item['style_tags'])}

Outfit idea:
{outfit}

Requirements:
- Write 2 to 4 sentences.
- Make it sound like a real social-media post, not a product listing.
- Mention the item.
- Include the price exactly as {price_text}.
- Mention {new_item['platform']} exactly once.
- Describe the specific vibe of the outfit.
- Do not use bullet points.
""".strip()

    response = generate(
        prompt,
        system=(
            "Write concise, natural social-media captions for second-hand "
            "fashion finds. Follow all requested factual details exactly."
        ),
    )

    return response or (
        f"{new_item['title']} for {price_text} on "
        f"{new_item['platform']} makes an easy second-hand find to build a "
        f"look around. The outfit gives it a wearable, styled vibe."
    )