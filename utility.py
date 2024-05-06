import os
import base64
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers.string import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

index_name = "docs"
embeddings = OpenAIEmbeddings()

vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

def format_data_for_openai(diffs, readme_content, commit_messages):
    prompt = None

    # Combine the changes into a string with clear delineation.
    changes = '\n'.join([
        f'file: {file["filename"]}\nDiff: \n{file["patch"]}\n'
        for file in diffs
    ])


    #  Add RAG pipeline here to embed changes and get most relevant docs from pinecone

    # Combine all commit messages
    commit_messages = '\n'.join(commit_messages) + '\n\n'

    # Decode the README content
    readme_content = base64.b64decode(readme_content.content).decode('utf-8')

    docs = get_docs_from_pinecone(changes)
    # Construct the prompt with clear instructions for the LLM.
    prompt = (
        "Please review the following code changes and commit messages from a GitHub pull request:\n"
        "Relevant docs:\n"
        f"{docs}"
        "Consider the documentation snippets provided, create a two to three sentence comment on each piece of documentation explaining its function for the PR\n"
    )

    print(prompt)

    return prompt

def get_docs_from_pinecone(changes):
    # Add Pinecone API call here to get most relevant documentation
    results = vectorstore.similarity_search(changes, k=3)
    
    return "\n".join(result.page_content for result in results)

def call_openai(prompt):
    client = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    try:
        messages = [
            {
                "role": "system", "content": "You are an AI assistant trained to help with commenting on PRs with relevant documentation updates."
            }, 
            {
                "role": "user", "content": prompt
            }
        ]
        response = client.invoke(input=messages)
        parser = StrOutputParser()
        content = parser.invoke(input=response)
        return content
    except Exception as e:
        print(f"Error making LLM call: {e}")


def comment_on_pr(pull_request, comment):
    comment_message = f"AI COMMENT:\n{comment}"
    pull_request.create_review(body=comment_message)
    return pull_request