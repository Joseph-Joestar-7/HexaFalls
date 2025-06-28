# Descriptive, Short, Formula-based
import os, re
import tiktoken
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain.schema import Document
load_dotenv()
ENCODER=tiktoken.get_encoding("cl100k_base")

def count_tokens(text): 
    return len(ENCODER.encode(text))

def extract_chapter_number(fname):
    m = re.search(r"chapter[_\-\s]?(\d+)", fname, re.IGNORECASE)
    return int(m.group(1)) if m else None

def ai_summarise(text, subject):
    parser = StrOutputParser()
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    chat_template = PromptTemplate(
        template='''
        You are an expert in {subject}. For a student, provide a well-structured notes in a descriptive way.
        The notes should be concise, clear, and contain technical terms for writing in exam paper. Try to keep the notes descriptive and informative keeping it as lengthy as possible.

        The notes should cover the key concepts, their definitions, features, important formulas, and relevant examples or applications with their understanding in 2-3 lines.
        Also if there are parts with examples explained, then try to provide the examples and its explanation in a concise way. Also highlight the important formulas in the notes.
        Also include a portion where difference between two similar concepts is explained in a tabular format.
        Dont include any irrelevant texts like page no., table of contents, etc.
        """
        {text}
        """
        ''',
        input_variables=["subject", "text"]
    )
    chain = chat_template | llm | parser
    return chain.invoke({"subject" : subject, "text": text})

def points_extractor(text):
    parser = StrOutputParser()
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    chat_template = PromptTemplate(
        template='''
        You are a expert in generating notes for the students. For a student, extract the key points or key headings from the given text from where questions can be asked in the exam.
        The points must be headings or sub-headings, not the full sentences. The points should be concise and clear, and contain technical terms for writing in exam paper.
        Like factors affecting the momentum, conservation of momentum, clockwise and anticlockwise moments, centre of gravity of an object, etc (These are just examples, not the actual points).
        \n\n\n
        Here is the text:
        {text}

        ''',
        input_variables=["text"]
    )
    chain = chat_template | llm | parser
    return chain.invoke({"text": text})

def getFinalNotes(docs, notes_type, tone, language="English"):
    parser = StrOutputParser()
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    if notes_type=="Descriptive":
        chat_template = PromptTemplate(
            template='''
            You are an expert in generating notes for the students in any language. Make me a final notes for a student by using the key points, summarised text and the original text in {language} language.
            Make the notes descriptive and informative, keeping it as lengthy as possible in a {tone} tone.
            The notes should cover the key concepts, their definitions, features, important formulas, and relevant examples or applications with their understanding in 2-3 lines.
            Also if there are parts with examples explained, then try to provide the examples and its explanation in a concise way. Also highlight the important formulas in the notes.
            Also include a portion where at least three differenciation is explained in a tabular format, like : Difference between torque and couple, Difference between clockwise and anticlockwise moments, Difference between centre of gravity and centre of mass, Difference betwwen uniform circular motion and uniform linear motion, etc.
            Keep the differentiation one after another not in a single table.
            Dont include any irrelevant texts like page no., table of contents, etc.
            Take the help from the key points and make changes in the summarised text to make it more informative and descriptive.
            
            Try to make the notes in a way that it can be used for writing in exam paper.
            Also add some extra information if you think it is necessary to make the notes more informative and descriptive.
            
            Here is the original text:
            {text}
            \n\n\n
            Here is the key points extracted from the text:
            {key_points}
            \n\n\n
            Here is the summarised text:
            {summary}
            \n\n\n
            ''',
            input_variables=["language", "tone", "text", "key_points", "summary"]
        )
    elif notes_type=="Short":
        chat_template = PromptTemplate(
            template='''
            You are an expert in generating notes for the students in any language. Make me a final notes for a student by using the key points, summarised text and the original text in {language} language.
            Make the notes concise and short, keeping it as brief as possible in a {tone} tone.
            The notes should cover the key concepts, their definitions, features, important formulas, and relevant examples.
            Also highlight the important formulas in the notes.
            Dont include any irrelevant texts like page no., table of contents, etc.
            Take the help from the key points and make changes in the summarised text to make it more informative and concise.
            
            Try to make the notes in a way that it can be used for writing in exam paper.
            Also add some extra information if you think it is necessary to make the notes more informative and concise.
            
            Here is the original text:
            {text}
            \n\n\n
            Here is the key points extracted from the text:
            {key_points}
            \n\n\n
            Here is the summarised text:
            {summary}
            \n\n\n
            ''',
            input_variables=["language", "tone", "text", "key_points", "summary"]
        )
    elif notes_type=="Formula-based":
        chat_template = PromptTemplate(
            template='''
            You are an expert in generating notes for the students in any language. Make me a final notes for a student by using the key points, summarised text and the original text in {language} language.
            Make the notes in a formula-based manner, keeping it as concise as possible in a {tone} tone.
            The notes should cover the topic name and their important formulas with the formula definition like defining the symbols used.
            Dont include any irrelevant texts like page no., table of contents, etc.
            Take the help from the key points and make changes in the summarised text to make it formula-based.
            
            Try to make the formula based notes in a way that it can be used for writing in exam paper.
            Also add some extra information about the formula if you think it is necessary to make the notes more informative and concise.
            
            Here is the original text:
            {text}
            \n\n\n
            Here is the key points extracted from the text:
            {key_points}
            \n\n\n
            Here is the summarised text:
            {summary}
            \n\n\n
            ''',
            input_variables=["language", "tone", "text", "key_points", "summary"]
        )

    chain = chat_template | llm | parser
    return chain.invoke({"language": language, 
                         "tone": tone,
                         "text": docs[0].page_content, 
                         "key_points": docs[0].metadata['key_points'], 
                         "summary": docs[0].metadata['summary']})


# docs=[]
# for fname in os.listdir("text_chapters"):
#     if not fname.endswith("01.txt"):
#         continue
#     chapter_number=extract_chapter_number(fname)
#     if chapter_number is None:
#         continue
#     with open(os.path.join("text_chapters", fname), "r", encoding="utf-8") as f:
#         text = f.read()
    
    
#     summary = ai_summarise(text)
#     key_points=points_extractor(text)
    
#     doc = Document(
#         page_content=text,
#         metadata={
#             "chapter": chapter_number,
#             "summary": summary,
#             "key_points": key_points,
#             "file_name": fname
#         }
#     )
#     docs.append(doc)

# final_notes=getFinalNotes(docs)
# print(final_notes)