import re
import os
import chromadb
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL,HANDBOOK_PATH,CHROMA_PATH,COLLECTION_NAME

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

client = chromadb.PersistentClient(path=CHROMA_PATH)

def _get_collection():
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},)

def load_handbook():
    
    if not os.path.exists(HANDBOOK_PATH):
        raise FileNotFoundError(f"Handbook not found: {HANDBOOK_PATH}")

    with open(HANDBOOK_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    return text.replace("\r\n", "\n").replace("\r", "\n")

SECTION_RE = re.compile(r"^\d+\.\s+\S")        
SUBSECTION_RE = re.compile(r"^\d+\.\d+\s+\S")  
MAX_CHARS = 1200

def _split_long(text, limit=MAX_CHARS):

    if len(text) <= limit:
        return [text]

    lines = text.split("\n")
    heading, body = lines[0], "\n".join(lines[1:])
    parts, current = [], ""

    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para:
            continue
        if current and len(current) + len(para) > limit:
            parts.append(f"{heading}\n{current}")
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para

    if current:
        parts.append(f"{heading}\n{current}")
    return parts


def create_chunks(text):
    
    chunks = []
    section_title = ""
    sub_title = None
    buffer = []

    def flush():
        body = "\n".join(buffer).strip()
        buffer.clear()
        if len(body) < 40:
            return
        header = f"{section_title} > {sub_title}" if sub_title else section_title
        for part in _split_long(f"{header}\n{body}"):
            chunks.append(part.strip())

    for raw in text.split("\n"):
        line = raw.strip()

        if SUBSECTION_RE.match(line):
            flush()
            sub_title = line
        elif SECTION_RE.match(line):
            flush()
            section_title = line
            sub_title = None
        elif line:
            buffer.append(line)
        else:
            buffer.append("")

    flush()
    return chunks


def build_vector_database(chunks=None):
    global_chunks = chunks or create_chunks(load_handbook())

    if not global_chunks:
        raise ValueError("No valid handbook chunks found.")

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = _get_collection()

    embeddings = embedding_model.encode(
        global_chunks,
        normalize_embeddings=True,
        show_progress_bar=False,)

    collection.add(
        ids=[f"chunk_{i}" for i in range(len(global_chunks))],
        embeddings=embeddings.tolist(),
        documents=global_chunks,)
    
    return len(global_chunks)


def ensure_database():
    chunks = create_chunks(load_handbook())
    collection = _get_collection()

    if collection.count() != len(chunks):
        return build_vector_database(chunks)

    return collection.count()



def retrieve_information(user_query, top_k=4):
    collection = _get_collection()

    query_embedding = embedding_model.encode(
        [user_query], normalize_embeddings=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,)
    
    return results.get("documents", [[]])[0]
