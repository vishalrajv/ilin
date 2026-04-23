"""FAISS retrieval logic with embedding and result formatting."""

# Developer: Vishal Raj V, Senior Engineer

import concurrent.futures
import numpy as np

from ilin.config import settings
from ilin.core.embedder import Embedder
from ilin.storage.vector_store import VectorStore


class Retriever:
    """Retrieves relevant chunks from a topic's vector index."""

    def __init__(self, embedder: Embedder | None = None):
        """Initialize retriever with optional shared embedder."""
        self.embedder = embedder or Embedder()

    def retrieve(self, topic_id: int, query: str, top_k: int | None = None) -> list[dict]:
        """Embed query and retrieve top-k matching chunks from topic index."""
        store = VectorStore(topic_id)
        query_embedding = self.embedder.embed_query(query)
        
        target_k = top_k or settings.retrieval_top_k
        fetch_k = target_k * 4 if settings.retrieval_use_mmr else target_k
        
        # Parallel searches (Dense + Sparse)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_dense = executor.submit(store.search, query_embedding, top_k=fetch_k, return_vectors=settings.retrieval_use_mmr)
            future_sparse = executor.submit(store.search_bm25, query, top_k=fetch_k)
            
            dense_results = future_dense.result()
            sparse_results = future_sparse.result()
            
        # Reciprocal Rank Fusion (RRF)
        rrf_k = 60
        rrf_scores = {}
        
        weight_dense = 0.6
        weight_sparse = 0.4
        
        items_by_id = {}
        
        for rank, item in enumerate(dense_results):
            idx = item["id"]
            if idx not in rrf_scores:
                rrf_scores[idx] = 0.0
            rrf_scores[idx] += weight_dense * (1.0 / (rrf_k + rank + 1))
            items_by_id[idx] = item
            
        for rank, item in enumerate(sparse_results):
            idx = item["id"]
            if idx not in rrf_scores:
                rrf_scores[idx] = 0.0
            rrf_scores[idx] += weight_sparse * (1.0 / (rrf_k + rank + 1))
            if idx not in items_by_id:
                items_by_id[idx] = item
                
        fused_results = []
        for idx, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
            item = items_by_id[idx].copy()
            item["score"] = score
            fused_results.append(item)
            
        results = fused_results

        if not settings.retrieval_use_mmr or len(results) <= target_k:
            final_results = results[:target_k]
        else:
            # Maximal Marginal Relevance (MMR) implementation
            mmr_lambda = 0.5
            selected = []
            unselected = list(range(len(results)))
            
            if unselected:
                selected.append(unselected.pop(0))
            
            while len(selected) < target_k and unselected:
                best_score = -np.inf
                best_idx = -1
                best_unselected_idx = -1
                
                selected_vectors = []
                for i in selected:
                    if "vector" in results[i]:
                        selected_vectors.append(results[i]["vector"])
                        
                if selected_vectors:
                    selected_vectors = np.array(selected_vectors)
                
                for i, unsel in enumerate(unselected):
                    cand = results[unsel]
                    sim_query = cand["score"]
                    
                    if "vector" in cand and len(selected_vectors) > 0:
                        sim_selected = np.dot(selected_vectors, cand["vector"]).max()
                    else:
                        sim_selected = 0.0
                    
                    mmr_score = mmr_lambda * sim_query - (1 - mmr_lambda) * sim_selected
                    
                    if mmr_score > best_score:
                        best_score = mmr_score
                        best_idx = unsel
                        best_unselected_idx = i
                        
                selected.append(best_idx)
                unselected.pop(best_unselected_idx)
                
            final_results = []
            for i in selected:
                item = results[i].copy()
                item.pop("vector", None)
                final_results.append(item)

        # Optional Cross-Encoder Re-Ranking
        if settings.retrieval_use_reranker and final_results:
            from sentence_transformers import CrossEncoder
            
            # Lazy load reranker (assumes model is downloaded locally to path)
            if not hasattr(self, "reranker"):
                self.reranker = CrossEncoder(settings.reranker_model_path, local_files_only=True)
                
            rerank_pairs = [[query, item["metadata"]["text"]] for item in final_results]
            rerank_scores = self.reranker.predict(rerank_pairs)
            
            print(f"[CROSS-ENCODER] Query: {query}")
            
            # Update scores, log vectors, and drop low scorers
            filtered_results = []
            for item, score in zip(final_results, rerank_scores):
                item["score"] = float(score)
                print(f"[CROSS-ENCODER] Score: {score:.4f} | Chunk: {item['metadata']['text'][:50]}...")
                # Threshold to drop hallucinations
                if score > -2.0:  # Threshold could be adjusted based on the specific cross-encoder model
                    filtered_results.append(item)
                else:
                    print(f"[CROSS-ENCODER] Dropped hallucination chunk due to low score: {score:.4f}")
                
            final_results = sorted(filtered_results, key=lambda x: x["score"], reverse=True)
            
        return final_results
