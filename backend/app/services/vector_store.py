import uuid
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, FilterSelector
from app.core.config import settings
from app.services.repo_parser import CodeChunk

VECTOR_SIZE = 384


class LocalHasher:
    def __init__(self):
        self.vectorizer = HashingVectorizer(
            n_features=VECTOR_SIZE,
            alternate_sign=False,
            norm="l2",
            analyzer="char_wb",
            ngram_range=(3, 5),
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        matrix = self.vectorizer.transform(texts).astype(np.float32)
        return matrix.toarray().tolist()


class VectorStore:
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url, timeout=30)
        self.embedder = LocalHasher()
        self.collection = settings.qdrant_collection

    def ensure_collection(self):
        collections = {c.name for c in self.client.get_collections().collections}
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )

    def delete_repo(self, repo_id: int):
        self.ensure_collection()
        self.client.delete(
            collection_name=self.collection,
            points_selector=FilterSelector(
                filter=Filter(must=[FieldCondition(key="repo_id", match=MatchValue(value=repo_id))])
            ),
            wait=True,
        )

    def upsert_chunks(self, repo_id: int, chunks: list[CodeChunk], batch_size: int = 64):
        self.ensure_collection()
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [f"{c.path}\n{c.text}" for c in batch]
            vectors = self.embedder.embed(texts)
            points = []
            for c, vector in zip(batch, vectors):
                pid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"repo:{repo_id}:{c.path}:{c.start_line}:{c.end_line}"))
                points.append(PointStruct(
                    id=pid,
                    vector=vector,
                    payload={
                        "repo_id": repo_id,
                        "path": c.path,
                        "start_line": c.start_line,
                        "end_line": c.end_line,
                        "text": c.text,
                    },
                ))
            self.client.upsert(collection_name=self.collection, points=points, wait=True)

    def search(self, repo_id: int, query: str, limit: int = 10) -> list[dict]:
        self.ensure_collection()
        vector = self.embedder.embed([query])[0]
        hits = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            query_filter=Filter(must=[FieldCondition(key="repo_id", match=MatchValue(value=repo_id))]),
            limit=limit,
            with_payload=True,
        ).points
        out = []
        for hit in hits:
            payload = hit.payload or {}
            out.append({
                "path": payload.get("path", "unknown"),
                "start_line": payload.get("start_line"),
                "end_line": payload.get("end_line"),
                "text": payload.get("text", ""),
                "score": float(hit.score),
            })
        return out


vector_store = VectorStore()
