def create_chunks(text, chunk_size=500, overlap=50):
    """
    Split text into chunks with overlap.

    Parameters:
        text (str): Cleaned text
        chunk_size (int): Number of words per chunk
        overlap (int): Number of overlapping words

    Returns:
        list: List of chunk dictionaries
    """

    words = text.split()

    chunks = []

    start = 0
    chunk_id = 1

    while start < len(words):

        end = start + chunk_size

        chunk_words = words[start:end]

        chunk_text = " ".join(chunk_words)

        chunks.append({
            "id": chunk_id,
            "text": chunk_text,
            "word_count": len(chunk_words)
        })

        chunk_id += 1

        start += (chunk_size - overlap)

    return chunks