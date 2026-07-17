import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

MODEL_NAME = "deepset/roberta-base-squad2"

tokenizer = None
model = None


def load_qa_model():
    global tokenizer, model

    if tokenizer is None or model is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)
        model.eval()

    return tokenizer, model


def answer_from_context(question, context):
    tokenizer, model = load_qa_model()

    inputs = tokenizer(
        question,
        context,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model(**inputs)

    start_scores = outputs.start_logits
    end_scores = outputs.end_logits

    start_index = torch.argmax(start_scores)
    end_index = torch.argmax(end_scores)

    if end_index < start_index:
        return "", 0.0

    answer_ids = inputs["input_ids"][0][start_index:end_index + 1]
    answer = tokenizer.decode(answer_ids, skip_special_tokens=True).strip()

    start_prob = torch.softmax(start_scores, dim=1)[0][start_index]
    end_prob = torch.softmax(end_scores, dim=1)[0][end_index]

    score = float((start_prob * end_prob).item())

    return answer, score


def get_best_answer(question, retrieved_chunks, min_score=0.35):
    best_answer = {
        "answer": "No confident answer found in the document.",
        "score": 0.0,
        "chunk": None
    }

    for item in retrieved_chunks:
        chunk = item["chunk"]
        context = chunk["text"]

        answer, score = answer_from_context(question, context)

        if not answer:
            continue

        if len(answer) < 3:
            continue

        if len(answer.split()) > 25:
            continue

        if score > best_answer["score"]:
            best_answer = {
                "answer": answer,
                "score": min(score, 1.0),
                "chunk": chunk
            }

    if best_answer["score"] < min_score:
        best_answer["answer"] = "No confident answer found in the document."

    return best_answer