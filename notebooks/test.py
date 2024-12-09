from transformers import pipeline

# Load a specific pre-trained model for text classification
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Define the texts to classify
texts = [
    "The weather is fantastic today!",
    "I am really worried about the upcoming exams.",
    "This new movie is terrible!",
    "This  if a beautifull day"
]

# Perform classification
results = classifier(texts)

# Display the results
for i, text in enumerate(texts):
    print(f"Text: {text}")
    print(f"Classification: {results[i]['label']} with score {results[i]['score']:.4f}")
    print()
