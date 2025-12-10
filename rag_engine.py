# rag_engine.py
import os
import uuid
from pathlib import Path
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from tqdm import tqdm
from pypdf import PdfReader

DEFAULT_EMBED_MODEL = 'all-MiniLM-L6-v2'

class Ingestor:
    def __init__(self, docs_folder='docs', persist_dir='chroma_db'):
        self.docs_folder = Path(docs_folder)
        self.persist_dir = persist_dir
        self.model_name = DEFAULT_EMBED_MODEL
        self.embedder = SentenceTransformer(self.model_name)
        self.client = chromadb.PersistentClient(path=persist_dir)
        try:
            self.col = self.client.get_collection('loan_docs')
        except Exception:
            self.col = self.client.create_collection('loan_docs')

    def read_pdf(self, filepath):
        reader = PdfReader(filepath)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

    def chunk_text(self, text, chunk_size=1000, overlap=200):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks

    def ingest_file(self, filepath):
        ext = filepath.suffix.lower()
        if ext == '.pdf':
            text = self.read_pdf(filepath)
        elif ext in ['.txt', '.md']:
            text = filepath.read_text(encoding='utf-8')
        else:
            print('Skipping unsupported:', filepath)
            return

        chunks = self.chunk_text(text)
        docs = []
        metadatas = []
        ids = []
        for i, c in enumerate(chunks):
            ids.append(str(uuid.uuid4()))
            docs.append(c)
            metadatas.append({'source': filepath.name, 'path': str(filepath.resolve()), 'chunk_index': i})

        print(f'Embedding {len(docs)} chunks from {filepath.name} ...')
        embeddings = self.embedder.encode(docs, show_progress_bar=True, convert_to_numpy=True)
        self.col.add(documents=docs, metadatas=metadatas, ids=ids, embeddings=embeddings.tolist())

    def ingest_all(self):
        files = list(self.docs_folder.glob('*.pdf')) + list(self.docs_folder.glob('*.txt')) + list(self.docs_folder.glob('*.md'))
        print('Found files:', [f.name for f in files])
        for f in tqdm(files):
            self.ingest_file(f)
        print('Chroma DB persisted to', self.persist_dir)


class RAG:
    def __init__(self, persist_dir='chroma_db', model_name=None):
        self.model_name = model_name or DEFAULT_EMBED_MODEL
        self.embedder = SentenceTransformer(self.model_name)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.col = self.client.get_collection('loan_docs')

    def query(self, text: str, top_k=5):
        emb = self.embedder.encode([text], convert_to_numpy=True)[0].tolist()
        results = self.col.query(query_embeddings=[emb], n_results=top_k, include=['documents','metadatas','distances'])
        docs = []
        for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
            docs.append({'text': doc, 'metadata': meta, 'distance': dist})
        return docs


def chat_with_gemini(system_prompt: str, user_prompt: str, context_chunks: List[Dict], language: str = 'en'):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise EnvironmentError('Set GEMINI_API_KEY in environment to use Gemini.')
    genai.configure(api_key=api_key)

    context_texts = []
    sources = []
    for c in context_chunks:
        md = c.get('metadata', {})
        src = md.get('source') or md.get('path') or 'unknown'
        context_texts.append(f"--- SOURCE: {src}\n{c['text']}\n")
        sources.append(src)
    context_combined = '\n\n'.join(context_texts)

    # Ensure Gemini responds in requested language and cites sources
    system_full = system_prompt + f"\n\nPlease respond in the language: {language}. Cite source filenames in square brackets at the end of statements where relevant."

    # Build full prompt combining system, context, and user query
    full_prompt = f"{system_full}\n\nContext (retrieved documents):\n{context_combined}\n\nUser question: {user_prompt}"

    # Use GenerativeModel API - using flash-latest for better quota limits
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content(
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=800
        )
    )

    # Extract text
    out = response.text if hasattr(response, 'text') else str(response)
    return out, list(dict.fromkeys(sources))
