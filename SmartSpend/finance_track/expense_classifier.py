from transformers import pipeline

_model = None

def classify_expense(text):
    global _model
    if _model is None:
        _model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    candidate_labels = [
        "Food & Beverage", "Transportation", "Groceries",
        "Entertainment", "Utilities", "Healthcare", "Other"
    ]
    result = _model(text, candidate_labels)
    return result["labels"][0]

classify_expense("Starbucks")

