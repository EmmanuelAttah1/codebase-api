from django.db.models import Q

from dotenv import load_dotenv, find_dotenv

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from .models import FileChunk, ProjectFile
from .prompt import main_prompt, user_prompt,prompt

import tiktoken


_ = load_dotenv(find_dotenv()) 
llm_name = "gpt-4" #"gpt-3.5-turbo"

encoding_name = "cl100k_base"

human_template = "{text}"
llm = ChatOpenAI(model_name=llm_name, temperature=0)
user_prompt_template = PromptTemplate.from_template(user_prompt)
system_message_prompt = SystemMessagePromptTemplate.from_template(prompt)
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)  
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

chain = LLMChain(
    llm=llm,
    prompt=chat_prompt,
    verbose=True
)


def count_token(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def formatUserQuery(chunk,name,dependency):
    #dependencies=str(dependency),
    query = user_prompt_template.format(chunk=chunk,chunk_name=name)

    return query


def getChunkDependency(dependencies_names,file,isHead):
    data = ''

    dependencies = dependencies_names.split(",")

    if not isHead:
        dependencies.insert(0,"head")

    for dependency in dependencies:
        try:
            file = ProjectFile.objects.get(name=file)
            chunk = FileChunk.objects.get(
                Q(name=dependency)
                &Q(file=file)
            )
            if len(chunk.doc) != 0:
                data += f"dependency name *{dependency}* \ndependency doc ```{chunk.doc}``` "
        except FileChunk.DoesNotExist:
            pass
        except ProjectFile.DoesNotExist:
            pass

    return data


async def generate_doc(info):    
    response = await chain.arun(info)

    return response


def process_chunk(chunk,dependency,context,name):
    all_context = f"{context}\n{dependency}"
    chunk_info = formatUserQuery(chunk,name,all_context)

    return chunk_info


prompt_count = count_token(prompt)