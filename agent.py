"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""
import re
import config
import trace
from tools import suggest_outfit, create_fit_card
from mcp_client import call_tool
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }



# Helper function

def _parse_query(query: str) -> dict:
    """Pull description, size, and max_price out of a plain-language query."""

    price_pattern = r"\bunder\s*\$?\s*(\d+(?:\.\d+)?)"
    size_pattern = r"\bsize\s+([a-zA-Z0-9./-]+)"

    price_match = re.search(price_pattern, query, re.IGNORECASE)
    size_match = re.search(size_pattern, query, re.IGNORECASE)

    max_price = float(price_match.group(1)) if price_match else None
    size = size_match.group(1) if size_match else None

    # Remove the filter phrases so only the description remains.
    description = re.sub(price_pattern, " ", query, flags=re.IGNORECASE)
    description = re.sub(size_pattern, " ", description, flags=re.IGNORECASE)

    # Clean up commas and extra spaces left behind.
    description = re.sub(r"\s+", " ", description)
    description = description.strip(" ,")

    return {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

# ── planning loop ─────────────────────────────────────────────────────────────

# def run_agent(query: str, wardrobe: dict) -> dict:
#     """
#     Run the planning loop once and return the finished session.
#     """
#     session = new_session(query, wardrobe)

#     iteration_count = 0

#     while True:
#         iteration_count += 1
#         trace.check_iterations(iteration_count)

#         # Step 1: Parse the user's query.
#         if not session["parsed"]:
#             session["parsed"] = _parse_query(session["query"])
#             continue

#         # Step 2: Search and branch on the result.
#         if session["selected_item"] is None:
#             session["search_results"] = call_tool(
#                 "search_listings",
#                 {
#                     "description": session["parsed"]["description"],
#                     "size": session["parsed"]["size"],
#                     "max_price": session["parsed"]["max_price"],
#                 },
#             )

#             # This is the required branch.
#             if not session["search_results"]:
#                 session["error"] = (
#                     "No listings matched your search. Try changing the item "
#                     "description, choosing a different size, or increasing "
#                     "your maximum price."
#                 )
#                 return session

#             # Read the result back out of the session.
#             session["selected_item"] = session["search_results"][0]
#             continue

#         # Step 3: Generate an outfit using the selected item from the session.
#         if session["outfit_suggestion"] is None:
#             try:
#                 session["outfit_suggestion"] = suggest_outfit(
#                     session["selected_item"],
#                     session["wardrobe"],
#                 )
#             except ModelUnavailable as exc:
#                 session["error"] = (
#                     f"The styling model couldn't be reached. {exc}"
#                 )
#                 return session

#             continue

#         # Step 4: Generate the fit card using values from the session.
#         if session["fit_card"] is None:
#             try:
#                 session["fit_card"] = create_fit_card(
#                     session["outfit_suggestion"],
#                     session["selected_item"],
#                 )
#             except ModelUnavailable as exc:
#                 session["error"] = (
#                     f"The styling model couldn't be reached. {exc}"
#                 )
#                 return session

#             return session

def run_agent(query: str, wardrobe: dict) -> dict:
    """Run the planning loop once and return the finished session."""
    session = new_session(query, wardrobe)

    iteration_count = 0

    while True:
        iteration_count += 1
        trace.check_iterations(iteration_count)

        # Step 1: Parse query.
        if not session["parsed"]:
            session["parsed"] = _parse_query(session["query"])

            trace.step(
                "parse_query",
                inputs=session["query"],
                returned=session["parsed"],
            )
            continue

        # Step 2: Search through MCP.
        if session["selected_item"] is None:
            search_inputs = {
                "description": session["parsed"]["description"],
                "size": session["parsed"]["size"],
                "max_price": session["parsed"]["max_price"],
            }

            session["search_results"] = call_tool(
                "search_listings",
                search_inputs,
            )

            if not session["search_results"]:
                trace.step(
                    "search_listings (via MCP)",
                    inputs=search_inputs,
                    returned=session["search_results"],
                    note="branch: empty search, stopping",
                )

                session["error"] = (
                    "No listings matched your search. Try changing the item "
                    "description, choosing a different size, or increasing "
                    "your maximum price."
                )
                return session

            trace.step(
                "search_listings (via MCP)",
                inputs=search_inputs,
                returned=session["search_results"],
                note="results found, continuing",
            )

            session["selected_item"] = session["search_results"][0]

            trace.step(
                "select_item",
                inputs=session["search_results"],
                returned=session["selected_item"],
            )
            continue

        # Step 3: Suggest outfit.
        if session["outfit_suggestion"] is None:
            try:
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"],
                    session["wardrobe"],
                )

                trace.step(
                    "suggest_outfit",
                    inputs={
                        "new_item": session["selected_item"],
                        "wardrobe": session["wardrobe"],
                    },
                    returned=session["outfit_suggestion"],
                )

            except ModelUnavailable as exc:
                session["error"] = (
                    f"The styling model couldn't be reached. {exc}"
                )

                trace.step(
                    "suggest_outfit",
                    inputs={
                        "new_item": session["selected_item"],
                        "wardrobe": session["wardrobe"],
                    },
                    returned=session["error"],
                    note="model unavailable, stopping",
                )

                return session

            continue

        # Step 4: Create fit card.
        if session["fit_card"] is None:
            try:
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"],
                    session["selected_item"],
                )

                trace.step(
                    "create_fit_card",
                    inputs={
                        "outfit": session["outfit_suggestion"],
                        "new_item": session["selected_item"],
                    },
                    returned=session["fit_card"],
                )

            except ModelUnavailable as exc:
                session["error"] = (
                    f"The styling model couldn't be reached. {exc}"
                )

                trace.step(
                    "create_fit_card",
                    inputs={
                        "outfit": session["outfit_suggestion"],
                        "new_item": session["selected_item"],
                    },
                    returned=session["error"],
                    note="model unavailable, stopping",
                )

                return session

            return session

# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
