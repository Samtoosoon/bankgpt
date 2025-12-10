import chromadb

# create in-memory chroma client
client = chromadb.EphemeralClient()

# create or load a collection
collection = client.get_or_create_collection(name="my_rag")

# insert vectors
collection.add(
    ids=["1", "2"],
    embeddings=[[0.1, 0.2, 0.3], [0.2, 0.4, 0.6]],
    documents=["hello world", "this is sample text"]
)

# query
result = collection.query(
    query_embeddings=[[0.1, 0.2, 0.25]],
    n_results=1
)

print(result)
