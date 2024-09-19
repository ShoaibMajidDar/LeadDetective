import json
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("openai_api_key")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")


def get_relationship(person_name: str, company_name: str):
    llm = ChatOpenAI(model = "gpt-4o-mini", temperature=0)
    search = GoogleSerperAPIWrapper(k = 15)
    search_text = f"{company_name} and {person_name}"
    search_result = search.run(search_text)

    template="""
Given the text below, identify and classify the relationship between {company} and {person}.
Output the result in the following format:
{{
    "relationship": "<classification>"
}}
Examples:
{{
    "relationship": "Manager"
}}
{{
    "relationship": "Developer"
}}

Text for analysis:
{search_result}
"""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke({"company": company_name, "person": person_name, "search_result":search_result})

    return json.loads(res)


