import os
import math
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from app.database.repository import Repository

load_dotenv()

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_v1 = math.sqrt(sum(x * x for x in v1))
    norm_v2 = math.sqrt(sum(x * x for x in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

class QAAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.embedding_model = "text-embedding-3-small"
        self.knowledge_base: List[Dict[str, Any]] = []

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            # Batch API call for embeddings
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return [[] for _ in texts]

    def get_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []

    def load_knowledge_base(self):
        """Loads digests from the repository and creates embeddings for them."""
        repo = Repository()
        digests = repo.get_recent_digests(hours=720) # Get all recent digests

        if not digests:
            self.knowledge_base = []
            return

        texts_to_embed = []
        for digest in digests:
            text = f"Title: {digest['title']}\nSummary: {digest['summary']}\nActionable Plan: {digest.get('actionable_plan', '')}"
            texts_to_embed.append(text)

        # Batch call embeddings
        embeddings = self.get_embeddings(texts_to_embed)

        self.knowledge_base = []
        for digest, text, embedding in zip(digests, texts_to_embed, embeddings):
            if embedding:
                self.knowledge_base.append({
                    "id": digest["id"],
                    "text": text,
                    "embedding": embedding,
                    "source": digest["url"]
                })
        print(f"Loaded {len(self.knowledge_base)} documents into knowledge base.")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return []

        scored_docs = []
        for doc in self.knowledge_base:
            score = cosine_similarity(query_embedding, doc["embedding"])
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]

    def answer_question(self, query: str) -> str:
        relevant_docs = self.search(query, top_k=3)

        if not relevant_docs:
            return "I don't have enough information in my knowledge base to answer this question."

        context = "\n\n".join([f"Source: {doc['source']}\n{doc['text']}" for doc in relevant_docs])

        prompt = f"""You are a helpful AI assistant. Answer the following question based ONLY on the provided context.
        If the context does not contain the answer, you MUST state explicitly: "I don't have enough information to answer this question." Do NOT hallucinate or use outside knowledge.

        Context:
        {context}

        Question: {query}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a factual assistant that answers questions only based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error answering question: {e}"

if __name__ == "__main__":
    qa = QAAgent()
    qa.load_knowledge_base()
    print("KB Loaded.")
