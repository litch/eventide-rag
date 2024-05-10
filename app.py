import streamlit as st
import random
import time

from dataclasses import dataclass, field
import os
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

st.title("Eventide chat")

@st.cache_resource
def load_model():
    print("Loaded the embeddings")
    embeddings = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-large")

    db = FAISS.load_local("eventide_docs_db", embeddings, allow_dangerous_deserialization=True)
    st.write(f"Indexed {db.index.ntotal} documents")
    return embeddings, db

embeddings, db = load_model()

# Initialize chat history
if "messages" not in st.session_state:
    system_prompt = """
    You are an expert in Domain Driven Design and Event Sourcing patterns.
    You are a strong proponent of the Eventide framework.
    Questions will come along with some Retrieval Augmented document pages that may or may not be relevant.

    Though you _may_ cite the documents if they are actually relevant, please do not do so unless they are directly relevant to the question at hand.
    Avoid providing document summaries or direct quotes unless they are directly relevant to the question at hand.
    """
    st.session_state.messages = [
        {"role": "system", "content": "You are an expert in Domain Driven Design and Event Sourcing patterns.  You are a strong proponent of the Eventide framework.  Questions will come along with some Retrieval Augmented document pages that may or may not be relevant"},
    ]

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

if "references" not in st.session_state:
    st.session_state.references = []

col1, col2 = st.columns([3, 2])

def do_rag(query):
    docs = db.similarity_search(query)
    print(docs)
    documentation = ""
    for doc in docs:
        documentation += f"{doc.metadata['source']} | {doc.page_content}\n\n"
        st.session_state.references.append(doc)
    redraw_references()
    print("Documentation: ", documentation)
    prompt = f"""Documents related to the query: {query}\n\n

        {documentation}

        Query: {query}

    """

    return call_openai(prompt)

def call_openai(prompt):
    client = ChatOpenAI(api_key = openai_api_key, model="gpt-3.5-turbo")
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        return client.stream(input=st.session_state.messages)
    except Exception as e:
        return f"An error occurred: {e}"

def redraw_references():
    with col2:
        for reference in st.session_state.references:
            draw_reference(reference)



def draw_reference(reference):
    """
    A container that has the title and source, and then a page_content that is markdown formatted and expandable
    """
    with st.container():
        m = reference.metadata
        title = " - ".join([m.get(k, "") for k in ["Header 1", "Header 2", "Header 3"]])
        st.subheader(title)
        st.caption(f"Source: {m.get('source', '')}")
        st.markdown(reference.page_content)



with col1:
    with st.container():
        history = st.container(height=400)
        # prompt = st.chat_input("Write something")

        with history:
            # Display chat messages from history on app rerun
            for message in st.session_state.display_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])


        # Accept user input
        if prompt := st.chat_input("What is up?"):
            # Add user message to chat history
            st.session_state.display_messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with history:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    stream = do_rag(prompt)
                    response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.display_messages.append({"role": "assistant", "content": response})