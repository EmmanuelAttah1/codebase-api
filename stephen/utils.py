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
from .prompt import main_prompt, user_prompt


_ = load_dotenv(find_dotenv()) 
llm_name = "gpt-3.5-turbo"

human_template = "{text}"
llm = ChatOpenAI(model_name=llm_name, temperature=0)
user_prompt_template = PromptTemplate.from_template(user_prompt)
system_message_prompt = SystemMessagePromptTemplate.from_template(main_prompt)
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)  
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

chain = LLMChain(
    llm=llm,
    prompt=chat_prompt,
    verbose=True
)


def formatUserQuery(chunk,dependency):

    query = user_prompt_template.format(dependencies=str(dependency),chunk=chunk)

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


def generate_doc(chunk,dependency,context):

    all_context = f"{context}\n{dependency}"

    query = formatUserQuery(chunk,all_context)

    # print("our query  ", query)
    
    response = chain.run(query)

    # print("my response ",response)

    return response
