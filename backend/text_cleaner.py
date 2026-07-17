import re
import unicodedata


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)

    text = text.replace("\t", " ")
    text = text.replace("\xa0", " ")

    # Add space between lowercase and uppercase joined words
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    # Add space after punctuation
    text = re.sub(r"([.,;:!?])([A-Za-z])", r"\1 \2", text)

    # Add space between letters and numbers
    text = re.sub(r"([A-Za-z])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", text)

    # Common PDF merged words
    text = text.replace("BERTuses", "BERT uses")
    text = text.replace("OpenAIGPT", "OpenAI GPT")
    text = text.replace("usesaleft", "uses a left")
    text = text.replace("withcheapermodels", "with cheaper models")
    text = text.replace("ontopof", "on top of")
    text = text.replace("thisrepresentation", "this representation")

    # Remove multiple spaces
    text = re.sub(r"[ ]{2,}", " ", text)

    # Remove multiple blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    # Remove spaces around newlines
    text = re.sub(r" *\n *", "\n", text)
    # Join words split by hyphen + newline
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Replace remaining newlines with spaces
    text = text.replace("\n", " ")

    # Remove repeated whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()