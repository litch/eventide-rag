# Initial development of querying the DB before porting it into the app

#%%
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

embeddings = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-large")

db = FAISS.load_local("eventide_docs_db", embeddings, allow_dangerous_deserialization=True)


print(db.index.ntotal)

query = "What is the correct format of the stream name for: bitcoind commands?"
docs = db.similarity_search(query)
print(docs)

def call_openai(prompt):
    client = ChatOpenAI(api_key = openai_api_key, model="gpt-3.5-turbo")
    messages = [
        {"role": "system", "content": "You are an expert in Domain Driven Design and Event Sourcing patterns.  You are a strong proponent of the Eventide framework.  Questions will come along with some Retrieval Augmented document pages that may or may not be relevant"},
        {"role": "user", "content": prompt}
    ]
    try:
        response = client.invoke(input=messages)
        parser = StrOutputParser()
        content = parser.invoke(input=response)
        return content
    except Exception as e:
        return f"An error occurred: {e}"

documentation = (f"{doc.metadata['source'] | doc.metadata['page_content']}\n\n" for doc in docs)


prompt = f"""Documents related to the query: {query}\n\n

{documentation}

Query: {query}

"""


response = call_openai(prompt)
print(response)
# %%# %%
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory

chat = ChatOpenAI(model="gpt-3.5-turbo")
demo_ephemeral_chat_history = ChatMessageHistory()

demo_ephemeral_chat_history.add_user_message("Hey there! I'm Nemo.")
demo_ephemeral_chat_history.add_ai_message("Hello!")
demo_ephemeral_chat_history.add_user_message("How are you today?")
demo_ephemeral_chat_history.add_ai_message("Fine thanks!")

demo_ephemeral_chat_history.messages

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability. The provided chat history includes facts about the user you are speaking with.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ]
)


chain = prompt | chat

chain_with_message_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: demo_ephemeral_chat_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

chain_with_message_history.invoke(
    {"input": "What's my name?"},
    {"configurable": {"session_id": "unused"}},
)

# %%
