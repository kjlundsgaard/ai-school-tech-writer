import os
import base64
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers.string import StrOutputParser

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

    # Construct the prompt with clear instructions for the LLM.
    prompt = (
        "Please review the following code changes and commit messages from a GitHub pull request:\n"
        "Code changes from Pull Request:\n"
        f"{changes}\n"
        "Commit messages:\n"
        f"{commit_messages}"
        "Consider the code changes, commit messages, and documentation snippets. Create a two to three sentence comment on the PR that describes how the dependencies are being used\n"
        "Relevant docs:\n"
    )

    print(prompt)

    return prompt

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


def comment_on_pr(pull_request, commit, path = "", position = 0):
    comment_message = "AI COMMENT"
    pull_request.create_comment(comment_message, commit, path, position)
    return pull_request