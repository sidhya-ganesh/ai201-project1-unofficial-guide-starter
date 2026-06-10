import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "upenn_reviews"
client = chromadb.PersistentClient(path="./chroma_db")

try:
    client.delete_collection(COLLECTION_NAME)
except:
    pass

collection = client.create_collection(COLLECTION_NAME)
model = SentenceTransformer("all-MiniLM-L6-v2")

docs = [
    ("Professor Ghrist at Penn teaches MATH 1400. His exams are hard but fair. Homework is harder than exams. The final is curved. He uses visual and topological approaches very different from AP Calculus.", "math1400_reviews.txt"),
    ("CIS 1200 with Zdancewic has a generous curve at end of semester. Midterms can feel discouraging. The final exam is cumulative. Past exams are the best study resource.", "cis120_reviews.txt"),
    ("Office hours at Penn are the most underused resource. Most professors see very few students outside exam weeks. Going regularly helps you stand out.", "general_upenn_advice.txt"),
    ("Angela Duckworth teaches PSYC 0001. Her course is rigorous with primary source readings. Exams test application not memorization. She brings world-class guest speakers. Rated 4.9/5.", "psyc001_reviews.txt"),
    ("To get off the waitlist at Penn, show up to the first lecture in person. Professors sometimes let in waitlisted students who attend. Penn has a two week shopping period.", "general_upenn_advice.txt"),
    ("CIS 1210 with Callison-Burch known as CCB is excellent. His exams focus on understanding not memorization. He drops the lowest homework grade.", "cis1210_reviews.txt"),
    ("Writing seminars at Penn are graded harshly. An A- is a good grade. Plagiarism cases go to the Honor Council regularly.", "writing_seminar_reviews.txt"),
    ("Adam Grant at Wharton is one of the most well-known professors. His lectures are energetic and evidence-based. Getting in is nearly impossible as a non-Wharton student.", "wharton_mgmt_reviews.txt"),
    ("PHYS 0150 with Thomson is great for pre-med students. Her practice exams closely mirror the real thing. She holds review sessions before each exam.", "phys150_reviews.txt"),
    ("Thomas Sugrue teaches HIST 1600. His lectures are performances — 75 minutes without notes. Readings are 80-100 pages per week. Exams are in-class essays.", "hist1600_reviews.txt"),
]

texts = [d[0] for d in docs]
metadatas = [{"source": d[1], "chunk_index": i} for i, d in enumerate(docs)]
ids = [f"chunk_{i}" for i in range(len(docs))]
embeddings = model.encode(texts).tolist()

collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
print(f"Done! {len(docs)} chunks stored.")