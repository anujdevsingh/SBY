import argparse
import json
import re
from pathlib import Path
from typing import Generator, List, Tuple

import faiss
from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from config import Config


def read_text_file(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def load_docs(doc_dir: Path) -> List[Tuple[str, str]]:
    docs = []
    for path in doc_dir.rglob('*'):
        if not path.is_file():
            continue
        if path.suffix.lower() in {'.txt', '.md'}:
            txt = read_text_file(path)
        elif path.suffix.lower() in {'.pdf'}:
            txt = read_pdf(path)
        else:
            continue
        docs.append((str(path), txt))
    print(f"Loaded {len(docs)} documents from {doc_dir}")
    return docs


def chunk_text(text: str, max_words: int = 120, overlap: int = 30) -> Generator[str, None, None]:
    words = re.split(r'\s+', text)
    start = 0
    while start < len(words):
        end = min(len(words), start + max_words)
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            yield chunk
        start = end - overlap
        if start < 0:
            start = end


def build_index_stream(
    docs: List[Tuple[str, str]],
    model_name: str,
    index_path: Path,
    meta_path: Path,
    batch_size: int = 256,
    max_words: int = 120,
    overlap: int = 30,
):
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    print("Model loaded. Starting embedding and indexing...")
    index = None
    meta: List[dict] = []
    buffer_texts: List[str] = []
    buffer_meta: List[dict] = []
    total_chunks = 0

    for source, text in docs:
        for i, chunk in enumerate(chunk_text(text, max_words=max_words, overlap=overlap)):
            buffer_texts.append(chunk)
            buffer_meta.append({"text": chunk, "source": source, "ref": f"{source}#chunk-{i}"})
            if len(buffer_texts) >= batch_size:
                embeddings = model.encode(buffer_texts, convert_to_numpy=True, normalize_embeddings=True).astype('float32')
                if index is None:
                    dim = embeddings.shape[1]
                    index = faiss.IndexFlatIP(dim)
                index.add(embeddings)
                meta.extend(buffer_meta)
                total_chunks += len(buffer_texts)
                print(f"Embedded chunks so far: {total_chunks}")
                buffer_texts.clear()
                buffer_meta.clear()

    if buffer_texts:
        embeddings = model.encode(buffer_texts, convert_to_numpy=True, normalize_embeddings=True).astype('float32')
        if index is None:
            dim = embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        meta.extend(buffer_meta)
        total_chunks += len(buffer_texts)
        print(f"Embedded chunks so far: {total_chunks}")

    if index is None:
        raise ValueError("No chunks were indexed. Check your documents.")

    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))
    with meta_path.open('w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Indexed {total_chunks} chunks -> {index_path}, meta -> {meta_path}")


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ingest policy documents into vector index.")
    parser.add_argument('--docs', default='policies', help='Directory with policy docs (txt/md/pdf)')
    parser.add_argument('--model', default=Config.POLICY_EMBED_MODEL, help='SentenceTransformer model name')
    parser.add_argument('--index', default=Config.POLICY_INDEX_PATH, help='Output FAISS index path')
    parser.add_argument('--meta', default=Config.POLICY_META_PATH, help='Output metadata json path')
    parser.add_argument('--batch-size', type=int, default=256, help='Embedding batch size to control memory use')
    parser.add_argument('--max-words', type=int, default=120, help='Max words per chunk')
    parser.add_argument('--overlap', type=int, default=30, help='Overlap words between chunks')
    args = parser.parse_args()

    doc_dir = Path(args.docs)
    if not doc_dir.exists():
        raise FileNotFoundError(f"Docs directory not found: {doc_dir}")

    docs = load_docs(doc_dir)
    if not docs:
        raise ValueError("No supported documents found (txt/md/pdf).")

    build_index_stream(
        docs,
        args.model,
        Path(args.index),
        Path(args.meta),
        batch_size=args.batch_size,
        max_words=args.max_words,
        overlap=args.overlap,
    )


if __name__ == '__main__':
    main()

