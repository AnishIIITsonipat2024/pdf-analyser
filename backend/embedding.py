from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def generate_embeddings(chunks):
    for chunk in chunks:
        embedding = model.encode(
            chunk["text"],
            convert_to_numpy=True
        )

        chunk["embedding"] = embedding

    return chunks


def generate_query_embedding(question: str):
    return model.encode(
        question,
        convert_to_numpy=True
    )