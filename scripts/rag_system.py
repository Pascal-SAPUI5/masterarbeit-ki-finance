import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import faiss
import ollama
import psutil
import pytesseract
import torch
import yaml
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PIL import Image
from rich.console import Console
from rich.progress import track
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF

# CPU Optimierungen
torch.set_num_threads(4)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
console = Console()

class PDFProcessor:
    def __init__(self):
        self.tesseract_config = "--oem 3 --psm 3"

    def extract_text_with_ocr(self, pdf_path: str) -> List[Dict[str, Any]]:
        doc = fitz.open(pdf_path)
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if not text.strip():  # OCR if no text
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img, lang="deu+eng", config=self.tesseract_config)
            pages.append({"page_num": page_num + 1, "text": text})
        doc.close()
        return pages

    def extract_metadata(self, pdf_path: str) -> Dict[str, str]:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "year": metadata.get("creationDate", "")[:4] or "",
            "doi": metadata.get("subject", "")  # Annahme, passe an
        }

    def chunk_text(self, text: str, size: int = 256) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=20)
        return splitter.split_text(text)

class RAGIndexer:
    def __init__(self, embedding_model: str, cpu_only: bool = True, index_path: str = "./indexes/"):
        self.device = "cpu" if cpu_only else "cuda"
        self.model = SentenceTransformer(embedding_model, device=self.device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index_path = Path(index_path)
        self.index_path.mkdir(exist_ok=True)
        self.metadata = []  # List of dicts: {"doc_id": int, "path": str, "chunk": str, "page": int}

    def add_document(self, pdf_path: str):
        processor = PDFProcessor()
        metadata = processor.extract_metadata(pdf_path)
        pages = processor.extract_text_with_ocr(pdf_path)
        
        doc_id = len(self.metadata)
        for page in pages:
            chunks = processor.chunk_text(page["text"])
            for chunk in chunks:
                embedding = self.model.encode(chunk)
                self.index.add(embedding.reshape(1, -1))
                self.metadata.append({
                    "doc_id": doc_id,
                    "path": pdf_path,
                    "chunk": chunk,
                    "page": page["page_num"],
                    "metadata": metadata
                })

    def index_directory(self, directory: str):
        pdfs = list(Path(directory).rglob("*.pdf"))
        for pdf in track(pdfs, description="Indexing PDFs..."):
            self.add_document(str(pdf))
        self.save_index()

    def save_index(self):
        faiss.write_index(self.index, str(self.index_path / "faiss_index"))
        with open(self.index_path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False)

    def load_index(self):
        index_file = self.index_path / "faiss_index"
        metadata_file = self.index_path / "metadata.json"
        if index_file.exists() and metadata_file.exists():
            self.index = faiss.read_index(str(index_file))
            with open(metadata_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            return True
        return False

class SemanticSearcher:
    def __init__(self, indexer: RAGIndexer):
        self.indexer = indexer

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_emb = self.indexer.model.encode(query)
        distances, indices = self.indexer.index.search(query_emb.reshape(1, -1), top_k)
        results = [self.indexer.metadata[idx] for idx in indices[0]]
        return self.rank_results(results, distances[0])

    def rank_results(self, results: List[Dict], distances: List[float]) -> List[Dict]:
        for res, dist in zip(results, distances):
            res["relevance"] = 1 - dist  # Simple ranking
        return sorted(results, key=lambda x: x["relevance"], reverse=True)

    def get_context(self, chunk: str, full_text: str) -> str:
        # Einfache Kontext-Extraktion: +/- 100 Zeichen
        idx = full_text.find(chunk)
        start = max(0, idx - 100)
        end = min(len(full_text), idx + len(chunk) + 100)
        return full_text[start:end]

class CitationGenerator:
    def generate_apa_citation(self, meta: Dict[str, str]) -> str:
        return f"{meta['author']} ({meta['year']}). {meta['title']}."

    def format_in_text(self, meta: Dict[str, str], page: int) -> str:
        return f"({meta['author']}, {meta['year']}, S. {page})"

    def create_bibliography(self, metas: List[Dict[str, str]]) -> str:
        return "\n".join(self.generate_apa_citation(m) for m in metas)

class RAGSystem:
    def __init__(self, config_path: str, cpu_only: bool = True):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.indexer = RAGIndexer(self.config["system"]["embedding_model"], cpu_only, self.config["paths"]["index_path"])
        # Lade existierenden Index falls vorhanden
        if not self.indexer.load_index():
            logging.info("No existing index found, will create new one if needed")
        self.searcher = SemanticSearcher(self.indexer)
        self.citer = CitationGenerator()
        self.llm_model = self.config["system"]["llm_model"]

    def query(self, text: str, top_k: int = 5) -> Dict[str, Any]:
        results = self.searcher.search(text, top_k)
        
        # Versuche LLM, falls zu viel RAM oder Ollama nicht verfügbar -> Fallback
        try:
            if psutil.virtual_memory().percent > 80:
                logging.warning("Hohe RAM-Nutzung, fallback zu simpler Suche")
                return self.format_response(results, text, use_llm=False)
            
            context = "\n".join(res["chunk"] for res in results)
            prompt = f"Beantworte basierend auf diesem Kontext: {context}\nFrage: {text}\nAntwort:"
            response = ollama.generate(model=self.llm_model, prompt=prompt, options={"num_thread": 4})["response"]
            return self.format_response(results, response)
        except Exception as e:
            logging.warning(f"LLM nicht verfügbar ({e}), nutze nur Retrieval")
            return self.format_response(results, text, use_llm=False)

    def format_response(self, results: List[Dict], answer: str, use_llm: bool = True) -> Dict[str, Any]:
        formatted = {
            "answer": answer,
            "sources": []
        }
        for res in results:
            meta = res["metadata"]
            source = {
                "information": res["chunk"],
                "source": f"[{meta['author']}, {meta['year']}, S. {res['page']}]",
                "context": self.searcher.get_context(res["chunk"], res["chunk"]),  # Erweitern bei Bedarf
                "citation": self.citer.format_in_text(meta, res["page"]),
                "related": []  # TODO: Implementiere verwandte
            }
            formatted["sources"].append(source)
        formatted["bibliography"] = self.citer.create_bibliography([res["metadata"] for res in results])
        return formatted

def main():
    parser = argparse.ArgumentParser(description="Lokales RAG-System für Masterarbeiten")
    subparsers = parser.add_subparsers(dest="command")

    index_parser = subparsers.add_parser("index")
    index_parser.add_argument("--path", required=True)
    index_parser.add_argument("--cpu-only", action="store_true", default=True)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--top-k", type=int, default=5)
    search_parser.add_argument("--cpu-only", action="store_true", default=True)

    batch_parser = subparsers.add_parser("batch")
    batch_parser.add_argument("--input", required=True)
    batch_parser.add_argument("--output", required=True)
    batch_parser.add_argument("--cpu-only", action="store_true", default=True)

    gui_parser = subparsers.add_parser("gui")
    gui_parser.add_argument("--port", type=int, default=8501)
    gui_parser.add_argument("--cpu-only", action="store_true", default=True)

    args = parser.parse_args()

    config_path = "config/rag_config.yaml"
    system = RAGSystem(config_path, args.cpu_only)

    if args.command == "index":
        system.indexer.index_directory(args.path)
    elif args.command == "search":
        result = system.query(args.query, args.top_k)
        console.print_json(data=result)
    elif args.command == "batch":
        with open(args.input, "r") as f:
            queries = f.readlines()
        results = [system.query(q.strip()) for q in queries]
        with open(args.output, "w") as f:
            json.dump(results, f)
    elif args.command == "gui":
        os.system(f"streamlit run scripts/rag_gui.py --server.port {args.port}")

if __name__ == "__main__":
    main() 