import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

#1. THE PROMPT TEMPLATE (Prompt Formatter)
#It takes raw user input and format it inot structured system/human format.
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert technical writer and your job is to simplify the complex concepts into simple 3 bullte points"),
    ("human", "Explain {concept} to junior engineer")
])

#2. THE LLM (the processor)
#Standard Gemini flash configuration
llm = GoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.0)

#3. THE OUTPUT PARSER (The clean-up crew)
#The LLM output a complex python object AIMessage, we just want raw string
parser = StrOutputParser()

#4. The LCEL - LangchainExpression Language
# Data Flow Left to Right: Dictionay ->  Prompt -> LLM -> String
chain = prompt | llm | parser

#5. THE EXECUTION
if __name__ == "__main__":
    target_concept = "BGP (Boarder Gateway Protocol) routing"
    print(f"[SYSTEM]: Currently running the LCEL chain for {target_concept}")

    #We pass a dictionary containig our variable to run the chain
    result = chain.invoke({"concept": target_concept})

    print(result)