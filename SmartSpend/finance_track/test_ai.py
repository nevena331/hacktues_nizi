from transformers import pipeline

# 1. Initialize the pipeline with a multilingual model (handles multiple languages better than bart-large-mnli).
#    If your text is mostly English, you can still use bart-large-mnli. 
#    But for Bulgarian or multilingual receipts, use an XNLI model like xlm-roberta.
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# 2. Sample JSON from your receipt scanner
receipt_data = {
    "receipt_date": "04.07.2017",
    "store_name": "Main Street Restaurant",
    "total": "29.01 USD"
}

# 3. Combine the fields into one text string
#    You can adapt this if you want to add more fields or if the text is in Bulgarian.
text = f"Store Name: {receipt_data['store_name']}. Date: {receipt_data['receipt_date']}. Total: {receipt_data['total']}."

# 4. Define candidate labels for classification
candidate_labels = ["Food & Beverage", "Transportation", "Groceries", "Healthcare", "Utilities", "Other"]

# 5. Run the classifier
result = classifier(text, candidate_labels)

# 6. Print the results
print("Input text:", text)
print("Classification result:", result)
