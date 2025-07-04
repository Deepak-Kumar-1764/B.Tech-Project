import os
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import nltk

# Download NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

# Load documents from the "data" directory
from llama_index.core import SimpleDirectoryReader
documents = SimpleDirectoryReader("data").load_data()

# Set file paths for saving/loading embeddings
embedding_file = "saved_embeddings.npy"
chunks_file = "saved_chunks.pkl"

# Check if we already have embeddings
new_files_added = len(documents) != len(np.load(embedding_file)) if os.path.exists(embedding_file) else True

if new_files_added:
    print("New files detected, generating new embeddings...")
    embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

    def get_text_embedding(text):
        return embedding_model.encode(text, convert_to_tensor=False)

    def chunk_document(text, chunk_by='paragraph'):
        if chunk_by == 'sentence':
            return nltk.sent_tokenize(text)
        elif chunk_by == 'paragraph':
            return text.split("\n\n")
        else:
            raise ValueError(f"Unsupported chunking method: {chunk_by}")

    chunks = []
    chunk_embeddings = []
    for doc in documents:
        doc_chunks = chunk_document(doc.text, chunk_by='paragraph')
        chunks.extend(doc_chunks)
        for chunk in doc_chunks:
            chunk_embeddings.append(get_text_embedding(chunk))

    chunk_embeddings = np.array(chunk_embeddings)

    # Save the embeddings and chunks for future use
    print("Saving embeddings and chunks...")
    np.save(embedding_file, chunk_embeddings)
    with open(chunks_file, 'wb') as f:
        pickle.dump(chunks, f)

else:
    print("No new files, loading saved embeddings and chunks...")
