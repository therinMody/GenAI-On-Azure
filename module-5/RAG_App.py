import os
from dotenv import load_dotenv
load_dotenv()

# Importing necessary modules from LangChain for integration with Azure and Streamlit
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from semantic_router.layer import RouteLayer, Route
from semantic_router.encoders import AzureOpenAIEncoder
from langchain.retrievers.multi_query import MultiQueryRetriever

# Setting up Streamlit page configuration
st.set_page_config(page_title="Generic Tech Shop Inc.", page_icon="🦜")
st.title("Customer Service Bot")

# Setting up Azure services for embeddings and vector search
embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
    azure_deployment="embeddings",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

index_name: str = "products-optimized"
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
    index_name=index_name,
    embedding_function=embeddings.embed_query,
)

# Setting up the GPT-4o OpenAI model for conversation handling
model = AzureChatOpenAI(
    azure_deployment="gpt4o",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)

# Defining routes for different types of customer queries
small_talk = Route(
    name="small_talk",
    utterances=[
        "Hey, how are you?", 
        "How's it going?",
        "Nice weather today"
    ],
)

headphones_questions = Route(
    name="headphones_questions",
    utterances=[
        "How much do the ClearSound X7 headphones cost?",
        "What headphones do you offer?",
        "What features does the SoundWave Elite 900 have?"
    ],
)

laptop_questions = Route(
    name="laptop_questions",
    utterances=[
        "How much do the TechMax UltraBook 14 laptop cost?",
        "What laptops do you offer?",
        "What features does the SwiftBook Pro 13 have?"
    ],
)

smartphone_questions = Route(
    name="smartphone_questions",
    utterances=[
        "How much do the TechMax NexTech Pro X smartphone cost?",
        "What smartphones do you offer?",
        "What features does the Galaxy Star G5 have?"
    ],
)

smartwatch_questions = Route(
    name="smartwatch_questions",
    utterances=[
        "How much do the FitGear 6X smartwatch cost?",
        "What smartwatchs do you offer?",
        "What features does the ChronoTrack A1 have?"
    ],
)

home_theater_questions = Route(
    name="home_theater_questions",
    utterances=[
        "How much does the Ultimate Home Theater System cost?",
        "What home theater packages do you offer?",
        "What features does the Ultimate Home Theater System have?"
    ],
)

# Creating a semantic router layer to handle different types of queries
routes = [small_talk, headphones_questions, laptop_questions, smartphone_questions, smartwatch_questions, home_theater_questions]
encoder = AzureOpenAIEncoder(api_key=os.getenv("AZURE_OPENAI_API_KEY"), deployment_name="embeddings", azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), api_version="2024-02-15-preview", model="text-embedding-ada-002")
rl = RouteLayer(encoder=encoder, routes=routes)

# Setting up templates for different product types to handle specific queries
laptop_prompt = """Your job is to answer questions on laptops
Answer the question based only on the following context and be sure to include citations (ie: laptop1 or laptop2):
{context}

Question: {question}
"""

smartphone_prompt = """Your job is to answer questions on smartphones
Answer the question based only on the following context and be sure to include citations (ie: smartphone1 or smartphone2):
{context}

Question: {question}
"""

headphone_prompt = """Your job is to answer questions on headphones
Answer the question based only on the following context and be sure to include citations (ie: headphones1 or headphones2):
{context}

Question: {question}
"""

smartwatch_prompt = """Your job is to answer questions on smartwatches
Answer the question based only on the following context and be sure to include citations (ie: smartwatch1 or smartwatch2):
{context}

Question: {question}
"""

home_theater_prompt = """Your job is to answer questions on the home theater package we sell
Answer the question based only on the following context and be sure to include citations (ie: hometheatersystem):
{context}

Question: {question}
"""

small_talk_prompt = ChatPromptTemplate.from_template("""Your job is a friendly customer service bot. Respond to the user in a 
friendly way and remind them we have lots of tech products like headphones, smartwatches, laptops, and more and ask how you can help.

Input: {input}
""")

chat_history_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
    "Original Question: {original_question}"
    "Chat History: {chat_history}"
)

retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=vector_store.as_retriever(), llm=model
)

# Function to determine the semantic layer based on the type of query
def semantic_layer(query: str):
    route = rl(query)
    result = None 

    if route.name == "laptop_questions":
        prompt = ChatPromptTemplate.from_template(laptop_prompt)
        retrieval_chain = (
            {"context": retriever_from_llm, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
        result = retrieval_chain.invoke(query)
    elif route.name == "headphones_questions":
        prompt = ChatPromptTemplate.from_template(headphone_prompt)
        retrieval_chain = (
            {"context": retriever_from_llm, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
        result = retrieval_chain.invoke(query)
    elif route.name == "smartphone_questions":
        prompt = ChatPromptTemplate.from_template(smartphone_prompt)
        retrieval_chain = (
            {"context": retriever_from_llm, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
        result = retrieval_chain.invoke(query)
    elif route.name == "smartwatch_questions":
        prompt = ChatPromptTemplate.from_template(smartwatch_prompt)
        retrieval_chain = (
            {"context": retriever_from_llm, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
        result = retrieval_chain.invoke(query)
    elif route.name == "home_theater_questions":
        prompt = ChatPromptTemplate.from_template(home_theater_prompt)
        retrieval_chain = (
            {"context": retriever_from_llm, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
        result = retrieval_chain.invoke(query)
    elif route.name == "small_talk":
        chain = small_talk_prompt | model | StrOutputParser()
        result = chain.invoke({"input": query})
    else:
        return "Sorry, I cannot help you with that."
    
    return result

# Class to maintain chat history
class ChatHistory:
    def __init__(self):
        self.queries = []

    def add_query(self, query):
        if len(self.queries) >= 10:
            self.queries.pop(0)
        self.queries.append(query)

    def get_queries(self):
        return self.queries
    
# Initializing chat history in Streamlit session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = ChatHistory()

chat_history = st.session_state.chat_history

# Function to process chat history for maintaining context in conversation
def process_chat_history(question, chat_history):
    prompt = ChatPromptTemplate.from_template(
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
        "Original Question: {question} "
        "Chat History: {chat_history}"
    )
    chain = prompt | model | StrOutputParser()
    result = chain.invoke({"question": question, "chat_history": chat_history})
    return result

# Handling message history in Streamlit session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Clearing message history button in Streamlit sidebar
if st.sidebar.button("Clear message history"):
    st.session_state.messages = []
    st.session_state.chat_history = ChatHistory()  # Reset chat history as well

# Avatars for different types of messages (human input and AI responses)
avatars = {"human": "user", "ai": "assistant"}

# Displaying message history and processing user queries
for msg in st.session_state.messages:
    st.chat_message(avatars[msg["type"]]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask me anything!")
if user_query:
    st.session_state.messages.append({"type": "human", "content": user_query})
    st.chat_message("user").write(user_query)
    chat_history.add_query(f"Human: {user_query}")
    result = process_chat_history(user_query, chat_history.get_queries())
    answer = semantic_layer(result)
    chat_history.add_query(f"AI: {answer}")
    st.session_state.messages.append({"type": "ai", "content": answer})
    st.chat_message("assistant").write(answer)