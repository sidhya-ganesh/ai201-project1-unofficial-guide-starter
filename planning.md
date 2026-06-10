# Planning: The Unofficial Penn Guide

## Domain
I chose **UPenn professor and course reviews** — student-generated knowledge about professors, exam formats, grading curves, and survival tips across Penn's major introductory courses. This knowledge is valuable because Penn's official sources (course catalog, registrar) tell you nothing about what a professor's exams actually look like, whether there's a curve, or which section to avoid. Students share this knowledge informally through Reddit, Rate My Professors, Discord servers, and class GroupChats — but it's scattered and hard to search systematically.

## Documents
10 source documents collected from Rate My Professors, PennCourseReview, and Reddit r/UPenn:

1. `cis120_reviews.txt` — CIS 1200 reviews for Zdancewic and Krakowsky
2. `cis1210_reviews.txt` — CIS 1210 reviews for Gandhi and Callison-Burch
3. `econ100_reviews.txt` — ECON 0100 reviews for Stein and Diebold
4. `math1400_reviews.txt` — MATH 1400 reviews for Ghrist and Kazdan
5. `writing_seminar_reviews.txt` — WRIT 0150 general advice and reviews
6. `psyc001_reviews.txt` — PSYC 0001 reviews for Gelperin and Duckworth
7. `wharton_mgmt_reviews.txt` — MGMT 1010 reviews for Adam Grant and Siggelkow
8. `phys150_reviews.txt` — PHYS 0150 reviews for Yodh and Thomson
9. `hist1600_reviews.txt` — HIST 1600 reviews for Sugrue and Powell
10. `general_upenn_advice.txt` — General Penn course registration and survival tips

## Chunking Strategy
**Chunk size:** Pre-curated focused chunks averaging 150-200 characters each, with no overlap needed since each chunk covers exactly one professor or topic.

My documents are review-style text — short opinion paragraphs averaging 3-5 sentences. Originally I planned 200-character chunks with 30-character overlap using an automated splitter, but due to memory constraints on my local machine I switched to pre-curated chunks. Each chunk is a hand-selected summary of one professor or topic, making every chunk fully self-contained and semantically rich. This actually improves retrieval quality because each embedding carries a clean, focused signal rather than a fragment of a larger review.

If I were scaling this to thousands of documents I would use the automated chunker with 300-character chunks and 50-character overlap.

## Retrieval Approach
**Embedding model:** `all-MiniLM-L6-v2` via sentence-transformers — runs locally, no API key, no rate limits, good semantic performance for English opinion text.

**Top-k:** 4 chunks per query. Review text is dense with specific opinions, so 4 chunks gives the LLM enough variety without overwhelming the context window with loosely-related material.

**Production tradeoffs I'd consider:**
- `text-embedding-3-large` (OpenAI) for higher accuracy but adds cost and API dependency
- `multilingual-e5-large` if the student body posts reviews in multiple languages
- Local models avoid rate limits but can't be updated without redeployment
- Context length matters if documents were longer; for short reviews, MiniLM's 256-token limit is fine

## Evaluation Plan
5 test questions with expected answers:

1. **Q:** What do students say about Professor Ghrist's exams in MATH 1400?
   **Expected:** Exams are hard but fair, homework is harder than exams, curve applied to final, uses visual/topological approach different from AP Calc.

2. **Q:** Is there a curve in CIS 1200?
   **Expected:** Yes — Zdancewic applies a generous curve at the end of the semester, but midterms can feel discouraging.

3. **Q:** How useful are office hours at Penn?
   **Expected:** Highly underused — most professors see very few students outside exam weeks; going regularly helps you stand out and get better help.

4. **Q:** What is Angela Duckworth's class like?
   **Expected:** High-effort, rigorous readings including primary sources, exams test application not memorization, guest speakers, highly rated (4.9/5).

5. **Q:** How do I get off the waitlist for a Penn course?
   **Expected:** Show up to the first lecture in person — professors sometimes let in waitlisted students who attend; also use the two-week shopping period.

## Anticipated Challenges
1. **Chunk boundary splits:** With automated chunking, a review mentioning both exam format AND grading curve might get split across chunks. The pre-curated approach eliminates this risk for the current corpus.
2. **Professor name variations:** Students use nicknames (CCB for Callison-Burch) — the embedding model may not link these, causing retrieval to miss relevant reviews when queries use nicknames.

## AI Tool Plan
- **Ingestion + chunking:** Prompted Claude with the Documents section and Chunking Strategy → implemented `ingest.py` with `chunk_text()` matching my spec.
- **Embedding + vector store:** Prompted Claude with the Retrieval Approach section → implemented `embed.py` using sentence-transformers and ChromaDB.
- **Generation:** Prompted Claude with grounding requirement and output format → implemented `query.py` with strict system prompt enforcing answers from retrieved context only.
- **Interface:** Prompted Claude with Gradio skeleton → wired to `query.py` ask() function in `app.py`.

## Architecture

```
Documents (10 .txt files)
        |
        v
[Ingestion + Cleaning]  ← ingest.py (load, strip boilerplate)
        |
        v
[Chunking]              ← pre-curated focused chunks, ~150-200 chars each
        |
        v
[Embedding]             ← all-MiniLM-L6-v2 (sentence-transformers)
        |
        v
[Vector Store]          ← ChromaDB (local, with source metadata)
        |
        v
[Retrieval]             ← top-4 semantic similarity search
        |
        v
[Generation]            ← Groq llama-3.3-70b-versatile
        |
        v
[Query Interface]       ← Gradio web UI (app.py)
```