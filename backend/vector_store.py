import faiss
import numpy as np


def create_faiss_index(chunks):
    """
    Create FAISS index from chunk embeddings.
    """

    embeddings = np.array(
        [chunk["embedding"] for chunk in chunks]
    ).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


def search_similar_chunks(question_embedding, index, chunks, top_k=5):
    """
    Search top-k similar chunks.
    """

    query_vector = np.array([question_embedding]).astype("float32")

    distances, indices = index.search(query_vector, top_k)

    results = []

    for distance, idx in zip(distances[0], indices[0]):
        results.append({
            "chunk": chunks[idx],
            "distance": float(distance)
        })

    return results