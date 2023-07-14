import openai
import logging

MODEL_NAME = "text-davinci-003"
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
REPHRASE_COUNT = 7

# logger = logging.getLogger(__name__)

def get_completion_from_messages(prompt, 
                                 model=MODEL_NAME,
                                 api_key=None, 
                                 temperature=0, max_tokens=500):
    openai.api_key = api_key

    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature, 
        max_tokens=max_tokens
    )
    return response

def get_empeddings(text, model=EMBEDDING_MODEL_NAME, api_key=None):
    openai.api_key = api_key
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def get_rephrase_prompt(query): 
    prompt = f"""
Your task is to rephrase a given question {REPHRASE_COUNT} times. Each question should mean the same
intention, but spelled in a unique style.

The output contains the list with the questions. You should prepare a list in the following format:
```
- Question 1
- Question 2
...
```

Here is a question: 
{query}
"""
    return prompt

def get_document_prompt(questions, document): 
    q_str = '\n\n'.join(questions)

    prompt = f"""
You are a list generator of answers and your task is to answer to each question based on facts from the document. The list of the questions:
###
{q_str}
###

The answer should contain only facts that in the document. 
If there is no useful information, the answer should be like "I'm sorry but I can't find any facts to that question".

The answers should be taken from the given document.
Here is the document:
###
{document}
###

The output format is a list of the answers. Provide a short answer with the reasoning steps. Example of output:
```
- Answer 1 
- Answer 2
...
```

The answers:
"""
    return prompt

def the_most_popular_prompt(answers):
    answers = '\n\n'.join(answers)

    prompt = f"""
Your task is to choose the most repetitive sentences from the given list with a reasoning steps. Here is the list of the answers:
###
{answers}
###

The output should be in the following format:
'''
The most repetitive answer is: 
<the one of the answers from the list>

The reason is:
<describe why the answer was chosen>
'''

The most repetitive answer is:
"""
    return prompt

def perform_list_response(resp):
    r = list(filter(lambda v: len(v.strip()) > 2, resp.choices[0]['text'].splitlines()))
    r = list(map(lambda v: v[len('- '):], r))
    return r

def get_completion_from_rephrase_prompt(query):
    resp = get_completion_from_messages(get_rephrase_prompt(query))

    r = list(filter(lambda v: len(v.strip()) > 2, resp.choices[0]['text'].splitlines()))
    r = list(map(lambda v: v[len('- '):], r))
    print(r)
# logger.info('\n' + colored(text.format(), 'blue'))
