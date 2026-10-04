# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

---

FitFindr takes a plain-language request for a second-hand clothing item and parses it into a description, optional size, and optional maximum price. It searches the local listings catalogue and, when a match is found, selects the first result and uses the user's wardrobe to generate two outfit suggestions around that item. It then creates a short social-media-style fit card that includes the item's price and selling platform. If no listings match, the agent stops before generating an outfit and tells the user what parts of the search they can change.

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** This tool searches the local clothing catalogue by description keywords with optional size and maximum price filters.
- **Inputs:** description: str, size: str | None = None, max_price: float |None = None <!-- name and type each: `max_price` (float), not "a price" -->
- **Returns:** A list of matching listing dictionaries, ranked by keyword match and then a lower price, each listing dictionary includes fields id, title, description, category, style_tags (list), size, condition, price (float), colors (list), brand (str or None), and platform
- **When it has nothing:** Returns an empty list `[]`

### `suggest_outfit`

- **What it does:** Suggests two outfits built around a selected listing, using items from the user's wardrobe when available.
- **Inputs:** new_item: dict (a listing), wardrobe: dict (with an items list)
- **Returns:** A non-empty string with two outfit suggestions, when the wardrobe has items, it names those pieces as written. 
- **When it has nothing:** With an empty wardrobe, returns general styling advice rather than raising or returning "".

### `create_fit_card`

- **What it does:** Writes a short social-media-style caption about the selected second-hand find and how it could be worn. 
- **Inputs:** outfit: str, new_item: dict (a listing)
- **Returns:** A string of two to four sentences that includes the price written with digits and the selling platform.
- **When it has nothing:** If outfit is empty or whitespace, returns a helpful fallback message instead of calling the model or raising an exception.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** After search_listings runs, the loop checks session["search_results"]. If the list is empty, it puts a helpful message in session["error"] telling the user what they could change in their search and returns the session without calling suggest_outfit. If results were found, it takes the first listing, stores it in session["selected_item"], and continues to suggest_outfit.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** The query will be parsed with regular expressions. The parser will look for a price phrase such as under $30 and store the number as max_price, and look for a size phrase such as size M or size XXS and store that value as size. Those filter phrases will then be removed from the query, and the remaining text will be used as the description. If no size or maximum price is present, that value will be None. The three parsed values will be stored in session["parsed"]. <!-- regex, string splitting, or asking the model — say which -->

**What moves through the session:** The original query and wardrobe start in the session. The parsed description, size, and max_price are stored in session["parsed"] and used to call search_listings. Its full return value is stored in session["search_results"]. If results exist, the first result is stored in session["selected_item"] and passed with session["wardrobe"] to suggest_outfit. That result is stored in session["outfit_suggestion"] and then passed with session["selected_item"] to create_fit_card. The final caption is stored in session["fit_card"]. If the search returns nothing, session["error"] is set and the run stops before the later tools are called. <!-- which fields, in what order -->

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'looking for a vintage graphic tee size M under $30'

```


  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two fun, Y2K-inspired outfit ideas built around your new butterfly baby tee, using pieces straight from your wardrobe:

### Outfit 1: Classic Y2K Streetwear
* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Baggy straight-leg jeans, dark wash
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

**Why it works:**
This is the ultimate nostalgic 2000s silhouette. The fitted, cropped nature of the butterfly tee contrasts perfectly with the relaxed, high-waisted fit of the baggy straight-leg jeans. Throwing on the slightly cropped vintage black denim jacket ties the whole streetwear vibe together while keeping you warm, and the chunky white sneakers match the crisp white base of the tee to complete the effortless, off-duty look.

---

### Outfit 2: Edgy Contrast & Grunge Touch
* **Top:** Y2K Baby Tee — Butterfly Print
* **Outerwear:** Black cropped zip hoodie
* **Bottoms:** Wide-leg khaki trousers
* **Shoes:** Black combat boots
* **Accessories:** Black crossbody bag

**Why it works:**
This look plays on the juxtaposition of sweet and edgy. The pink and purple butterfly graphics on the baby tee pop against the neutral wide-leg khaki trousers. Layering the black cropped zip hoodie on top adds a cool, utilitarian edge, which is anchored down by the lace-up black combat boots. It’s a great way to take a hyper-feminine Y2K piece and ground it with a tougher, street-smart aesthetic.

  Fit card: Fly into the Y2K aesthetic with this super cute vintage butterfly baby tee, up on my depop now for just $18! Style it with baggy dark-wash jeans and a black denim jacket for the ultimate nostalgic streetwear vibe. Grab it before it's gone!


**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```
[{'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}]  

```
$ python -c "from tools import suggest_outfit; ..."

```

Here are two outfit suggestions built around your new vintage Levi's 501 jeans, using pieces straight from your wardrobe:

### Outfit 1: Casual Streetwear Classic
* **Top:** White ribbed tank top (id: w_003)
* **Outerwear:** Vintage black denim jacket (id: w_006)
* **Shoes:** Chunky white sneakers (id: w_007)
* **Accessories:** Brown leather belt (id: w_009), Black crossbody bag (id: w_010)

**Why this works:**
This is an effortless, everyday look that leans into the streetwear style tag of your new 501s. Pairing the medium-wash denim with the slightly cropped vintage black denim jacket creates a cool, balanced double-denim moment. The fitted white ribbed tank top provides a sharp contrast to the straight-leg structure of the jeans, while the chunky white sneakers and black crossbody bag tie the casual streetwear vibe together. Use the brown leather belt to add a nice touch of contrast at the waist.

### Outfit 2: Cozy Grunge-Inpsired Layers
* **Top:** Oversized grey crewneck sweatshirt (id: w_004)
* **Shoes:** Black combat boots (id: w_008)
* **Accessories:** Black crossbody bag (id: w_010)

**Why this works:**
This combination plays on proportions and texture. The really oversized grey crewneck sweatshirt contrasts brilliantly with the classic, structured fit of the vintage Levi's. Because the sweatshirt drops below the hip and the jeans have a touch of fading at the knees, the look gets an effortlessly cool, laid-back edge. Tying it together with the black combat boots and black crossbody bag adds a subtle grunge twist that grounds the medium blue wash of the denim.

```
$ python -c "from tools import create_fit_card; ..."

```

Nothing beats a classic pair of vintage Levi's 501 jeans, especially when they come with that perfect medium wash and effortlessly cool knee fading. Grab these for just $38 before they’re gone! Just toss them on with your favorite white sneakers for a timeless, laid-back street style look. Head over to my depop to snag them today.

#vintage #classic #denim #streetwear

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked AI how to implement the size filter in search_listings without using a plain substring match, because the starter warned that a search for S could accidentally match US 9 and L could match XL.
- *What came back:* AI suggested using a regular-expression-based size helper that treats the requested size as a complete size label or component, so M can match M or S/M without matching unrelated text.
- *What I changed:* I added a _size_matches() helper to tools.py and used it when the optional size filter is provided instead of using a simple in substring check.

**Moment 2**

- *What I asked for:* I asked AI to help check the query parsing and empty-search branch in run_agent() using the test query designer ballgown size XXS under $5.
- *What came back:* The first test showed max_price as None because PowerShell removed $5 before Python received the query. AI identified that the shell, not the parser, was causing the problem and suggested constructing the dollar sign with chr(36) for the test command.
- *What I changed:* I changed the terminal test command and ran it again. The session then correctly showed size as XXS, max_price as 5.0, an empty search_results list, fit_card still set to None, and a helpful error message, so I did not change the working branch logic.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
