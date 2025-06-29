# rag_chat.py

import warnings
from dotenv import load_dotenv

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Correct chain imports:
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
warnings.filterwarnings("ignore")

gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
model             = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                                           convert_system_message_to_human=True)

store = {}
MAX_HISTORY_LENGTH = 20

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Return a ChatMessageHistory for this session_id, trimming older entries.
    """
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    history = store[session_id]
    if len(history.messages) > MAX_HISTORY_LENGTH:
        history.messages = history.messages[-MAX_HISTORY_LENGTH:]
    return history

_placeholder_doc = Document(page_content="__PLACEHOLDER__", metadata={})
_placeholder_splits = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                   chunk_overlap=200).split_documents([_placeholder_doc])
_vectorstore = FAISS.from_documents(_placeholder_splits, embedding=gemini_embeddings)
_retriever  = _vectorstore.as_retriever()

_system_prompt = (
    "You are an assistant for doubt‑solving students. Use retrieved context first, "
    "but you may answer from general knowledge. If unknown, say so.\n\n{context}"
)
_retriever_prompt = (
    "Given a chat history and the latest question which may refer to prior messages, "
    "reformulate it as a standalone question. Do not answer it here."
)

_contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", _retriever_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

_qa_prompt = ChatPromptTemplate.from_messages([
    ("system", _system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

_history_aware_retriever     = create_history_aware_retriever(model, _retriever, _contextualize_q_prompt)
_qa_chain                   = create_stuff_documents_chain(model, _qa_prompt)
_rag_chain                  = create_retrieval_chain(_history_aware_retriever, _qa_chain)
conversational_rag_chain    = RunnableWithMessageHistory(
    _rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer"
)

def initialize_index_from_text(text: str, metadata: dict = None):
    """
    (Optional) Call this once if you want to index a large corpus of notes up‑front.
    You can skip this if you build your own vectorstore per‑document on the fly.
    """
    doc = Document(page_content=text, metadata=metadata or {})
    splits = RecursiveCharacterTextSplitter(chunk_size=1000,
                                            chunk_overlap=200).split_documents([doc])
    global _vectorstore, _retriever, _history_aware_retriever, conversational_rag_chain
    _vectorstore = FAISS.from_documents(splits, embedding=gemini_embeddings)
    _retriever  = _vectorstore.as_retriever()
    _history_aware_retriever = create_history_aware_retriever(model,
                                                             _retriever,
                                                             _contextualize_q_prompt)
    _qa_chain                = create_stuff_documents_chain(model, _qa_prompt)
    _rag_chain               = create_retrieval_chain(_history_aware_retriever, _qa_chain)
    conversational_rag_chain = RunnableWithMessageHistory(
        _rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

def chat_response(user_input: str, session_id: str) -> str:
    """
    Given a new user_input and a session ID (e.g. user_id),
    invoke the conversational RAG chain and return the assistant's reply.
    """
    res = conversational_rag_chain.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )
    return res["answer"]
