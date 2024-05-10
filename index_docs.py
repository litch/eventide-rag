from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter

from dotenv import load_dotenv
import os

openai_api_key = os.getenv("OPENAI_API_KEY")

loader = DirectoryLoader('docs', glob="**/*.md", show_progress=True, use_multithreading=True, loader_cls=TextLoader)
embeddings = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-large")

docs = loader.load()

for doc in docs:
    # For the page_content, remove everything before the first # to remove sidebar bs
    doc.page_content = doc.page_content[doc.page_content.find("#"):]

text_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ]
    )

print(docs[0])

split_docs = []
for doc in docs:
    split_doc_content = text_splitter.split_text(doc.page_content)
    for d in split_doc_content:
        # combine the metadata from the original doc with the split doc (d)
        d.metadata = d.metadata | doc.metadata
        d.metadata['root_url'] = "http://docs.eventide-project.org/"

    split_docs.extend(split_doc_content)

print(split_docs[0:3])

print(f"Loaded {len(split_docs)}")

# vectors = embedder.embed_documents(split_docs)

# print(f"Embedded {len(vectors)}")

db = FAISS.from_documents(split_docs, embeddings)

print(f"Indexed {len(split_docs)}")

# save this db to disk

db.save_local("eventide_docs_db")

# print(db.index.ntotal)

# query = "Can you suggest event names for a bank account creation event?"
# docs = db.similarity_search_with_score(query)

# print(docs)