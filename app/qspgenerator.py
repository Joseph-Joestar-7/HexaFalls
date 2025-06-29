from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()

def question_paper(subject, marks, hour, difficulty_level, topics):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    parser=StrOutputParser()
    prompt = PromptTemplate(
        template='''
You are an expert in generating question papers of any class and any subject.
So make a question paper of class 10 of subject {subject}.
The total marks of the paper must be {marks}.
The duration is of {hour} time.
The difficulty level of the paper must be {difficulty_level}.
The paper must contain 25% of overall marks of MCQs.
Next, there would be a section of Short Type Answer Question of 25% of total marks.
Next, there would be a section of Long Type Answer Question of 25% of total marks.
Next, there would be a section of Numerical type Question of 25% of total marks.
Here are the topics of the question paper from where the questions are to be asked.
Topics : {topics}
''',
        input_variables=["subject", "marks", "hour", "difficulty_level", "topics"]
    )

    chain=prompt|llm|parser

    return chain.invoke(
        {"subject": subject,
        "marks": marks,
        "hour": hour,
        "difficulty_level":difficulty_level,
        "topics":topics
    })