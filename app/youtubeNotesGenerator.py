import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()

def get_transcript(video_id, languages=['en', 'hi']):
    try:
        transcript_list=YouTubeTranscriptApi.get_transcript(video_id, languages)
        transcript=" ".join([item['text'] for item in transcript_list])
        print(transcript)

    except TranscriptsDisabled:
        print(f"Transcript is disabled for video ID: {video_id}")

    return transcript

def language_convertor(transcript, target_language='en'):
    llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    chat_template=PromptTemplate(
    template="""
        You are a helpful language change agent. You will be given a Youtube transcript.
        Your task is to convert the transctript to a more readable format in {target_language}.
        \n\n\n
        Here is the transcript:
        {transcript}""", 
        input_variables=["target_language", "transcript"]
    )
    parser=StrOutputParser()
    chain=chat_template | llm | parser
    return chain.invoke({"target_language": target_language, "transcript": transcript})

def notes_generator(text, notes_type, tone):
    llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    if notes_type == "Descriptive":
        notes_template=PromptTemplate(
            template="""
            You are an expert teacher and a researcher. You will be given a Youtube transcript.
            Your task is to make the notes in descriptive and informative, keeping it as lengthy as possible in a {tone} tone.
            The notes should cover the key concepts, their definitions, features, important formulas, and relevant examples or applications with their understanding in 2-3 lines.
            Also if there are parts with examples explained, then try to provide the examples and its explanation in a concise way. Also highlight the important formulas in the notes.
            Also include a portion where at least three differenciation is explained in a tabular format, eg. : Difference between torque and couple, Difference between clockwise and anticlockwise moments, Difference between centre of gravity and centre of mass (Use differences as per context not these ones)
            Keep the differentiation one after another not in a single table.
            Dont include any irrelevant texts like page no., table of contents, etc.
            
            Try to make the notes in a way that it can be used for writing in exam paper.
            Also add some extra information if you think it is necessary to make the notes more informative and descriptive.
            \n\n\n
            Here is the transcript:
            {result}""",
            input_variables=["tone", "result"]
        )
    elif notes_type == "Short":
        notes_template=PromptTemplate(
            template="""
            You are an expert teacher and a researcher. You will be given a Youtube transcript.
            Your task is to make the notes in concise and short, keeping it as brief as possible in a {tone} tone.
            The notes should cover the key concepts, their definitions, features, important formulas, and relevant examples or applications with their understanding in 1-2 lines.
            Also if there are parts with examples explained, then try to provide the examples and its explanation in a concise way. Also highlight the important formulas in the notes.
            Dont include any irrelevant texts like page no., table of contents, etc.
            
            Try to make the notes in a way that it can be used for writing in exam paper.
            Also add some extra information if you think it is necessary to make the notes more informative and concise.
            \n\n\n
            Here is the transcript:
            {result}""",
            input_variables=["tone", "result"]
        )

    elif notes_type=="Formula-based":
        notes_template=PromptTemplate(
            template="""
            You are an expert teacher and a researcher. You will be given a Youtube transcript.
            Your task is to make the notes in a formula-based manner, keeping it as concise as possible in a {tone} tone.
            The notes should cover the topic name and their important formulas with the formula definition like defining the symbols used.
            Dont include any irrelevant texts like page no., table of contents, etc.
            
            Try to make the formula based notes in a way that it can be used for writing in exam paper.
            Also add some extra information about the formula if you think it is necessary to make the notes more informative and concise.
            \n\n\n
            Here is the transcript:
            {result}""",
            input_variables=["tone", "result"]
        )
    parser=StrOutputParser()
    chain=notes_template | llm | parser
    notes=chain.invoke({"tone": tone, "result": text})
    return notes


# youtube_video_id="WGUNAJki2S4"
# transcript=get_transcript(youtube_video_id)
# if transcript:
#     converted_transcript=language_convertor(transcript, target_language='en')
    
#     notes_type="short"  
#     tone="funny"  
#     notes=notes_generator(converted_transcript, notes_type, tone)
    
#     print("Generated Notes:")
#     print(notes)


