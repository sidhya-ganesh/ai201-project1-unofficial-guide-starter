# The Unofficial Penn Guide
A RAG system that makes student-generated knowledge about UPenn courses and professors searchable and answerable.

## Domain and Document Sources
**Domain:** UPenn professor and course reviews — student knowledge about exam formats, grading curves, professor teaching styles, and campus survival tips. This knowledge is valuable because Penn's official sources tell you nothing about whether a curve exists, which section to take, or what professors actually test on. Students share this informally through Reddit, Rate My Professors, and Discord — but it's scattered and hard to search.

**Sources:**
- `cis120_reviews.txt` — Rate My Professors / PennCourseReview: CIS 1200 reviews for Zdancewic and Krakowsky
- `cis1210_reviews.txt` — Rate My Professors / PennCourseReview: CIS 1210 reviews for Gandhi and Callison-Burch
- `econ100_reviews.txt` — Rate My Professors / PennCourseReview: ECON 0100 reviews for Stein and Diebold
- `math1400_reviews.txt` — Rate My Professors / PennCourseReview: MATH 1400 reviews for Ghrist and Kazdan
- `writing_seminar_reviews.txt` — Reddit r/UPenn: WRIT 0150 general advice
- `psyc001_reviews.txt` — Rate My Professors / PennCourseReview: PSYC 0001 reviews for Gelperin and Duckworth
- `wharton_mgmt_reviews.txt` — Reddit r/UPenn / Wharton forums: MGMT 1010 reviews for Grant and Siggelkow
- `phys150_reviews.txt` — Rate My Professors / PennCourseReview: PHYS 0150 reviews for Yodh and Thomson
- `hist1600_reviews.txt` — Reddit r/UPenn: HIST 1600 reviews for Sugrue and Powell
- `general_upenn_advice.txt` — Reddit r/UPenn / Penn Discord: General registration and survival tips

## Chunking Strategy and Reasoning
**Strategy:** Pre-curated focused chunks averaging 150-200 characters each.

Originally planned automated 200-character chunks with 30-character overlap. Due to memory constraints on local hardware during development, switched to pre-curated chunks where each chunk covers exactly one professor or topic. This improved retrieval quality because each embedding carries a clean, focused semantic signal rather than a mid-sentence fragment. For a production system with thousands of documents I would use automated chunking at 300 characters with 50-character overlap.

## Sample Chunks
**Chunk 1** (source: math1400_reviews.txt)
> Professor Ghrist at Penn teaches MATH 1400. His exams are hard but fair. Homework is harder than exams. The final is curved. He uses visual and topological approaches very different from AP Calculus.

**Chunk 2** (source: cis120_reviews.txt)
> CIS 1200 with Zdancewic has a generous curve at end of semester. Midterms can feel discouraging. The final exam is cumulative. Past exams are the best study resource.

**Chunk 3** (source: general_upenn_advice.txt)
> Office hours at Penn are the most underused resource. Most professors see very few students outside exam weeks. Going regularly helps you stand out.

**Chunk 4** (source: psyc001_reviews.txt)
> Angela Duckworth teaches PSYC 0001. Her course is rigorous with primary source readings. Exams test application not memorization. She brings world-class guest speakers. Rated 4.9/5.

**Chunk 5** (source: general_upenn_advice.txt)
> To get off the waitlist at Penn, show up to the first lecture in person. Professors sometimes let in waitlisted students who attend. Penn has a two week shopping period.

## Embedding Model
**Model used:** `all-MiniLM-L6-v2` via sentence-transformers. Runs locally — no API key, no rate limits, no cost.

**Production tradeoffs:**
- `text-embedding-3-large` (OpenAI) would give higher accuracy but adds cost and API dependency
- `multilingual-e5-large` would support non-English reviews
- Local models avoid rate limits but require redeployment to update
- MiniLM's 256-token context limit is fine for short reviews but would be a constraint for longer documents

## Retrieval Test Results

**Query 1:** What do students say about Professor Ghrist's exams?
Top chunks retrieved: math1400_reviews.txt, cis1210_reviews.txt, cis120_reviews.txt, hist1600_reviews.txt
**Why relevant:** The math1400 chunk directly describes Ghrist's exam style. The other chunks were retrieved because they also discuss exam difficulty and curves — semantically similar language even from different courses.

**Query 2:** Is there a curve in CIS 1200?
Top chunks retrieved: cis1210_reviews.txt, math1400_reviews.txt, cis120_reviews.txt, phys150_reviews.txt
**Why relevant:** The cis120 chunk directly answers the question. Other chunks retrieved because they also mention curves — the semantic similarity of "curve" language pulls related content.

**Query 3:** How useful are office hours at Penn?
Top chunks retrieved: general_upenn_advice.txt, math1400_reviews.txt, writing_seminar_reviews.txt
**Why relevant:** The general_upenn_advice chunk directly addresses office hours. This is the strongest retrieval result — exact topic match with high confidence.

## Grounded Generation
Grounding is enforced through the system prompt in `query.py`: