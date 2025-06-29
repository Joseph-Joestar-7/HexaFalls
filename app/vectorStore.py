from langchain import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains import LLMChain

def generate_document_quiz(text: str, file_context: str, question_level: str, number: int):
  embeddings=GoogleGenerativeAIEmbeddings(model="models/embedding-001")
  model=ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=1.0)
  prompt = PromptTemplate(
  input_variables=["question_level","number","context"],
  template="""
    You are an expert examiner and question paper setter.
    Create a challenging {question_level}‑level question paper from the notes below. 
    Use unknown examples outside the book to ask reasoning‑type questions.
    Everything must remain within the syllabus. All questions should be creative, challenging, 
    and not common.

    Generate exactly {number} MCQs (1 mark each) to test conceptual understanding.

    Notes:
    {context}
    """
    )
  doc=Document(page_content=text, metadata={"source":"Document Notes", "title":file_context})
  splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
  splits=splitter.split_documents([doc])
  vs=FAISS.from_documents(splits, embedding=embeddings)
  retriever=vs.as_retriever()

  docs=retriever.get_relevant_documents("Generate Quiz")
  context="\n\n".join(d.page_content for d in docs)

  chain=LLMChain(llm=model, prompt=prompt)
  quiz=chain.run({
    "question_level": question_level,
    "number":         number,
    "context":        context
  })

  return quiz

# Example usage:
if __name__ == "__main__":
  sample_text=open("my_notes.txt").read()
  quiz = generate_document_quiz(
    sample_text,
    file_context="Chapter 1: Forces",
    question_level="Advanced",
    number=5
  )
  print(quiz)
