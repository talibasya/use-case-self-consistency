import streamlit as st
from enum import Enum

from prompts import get_completion_from_messages, perform_list_response, get_document_prompt, the_most_popular_prompt, get_rephrase_prompt

class TAB_NAMES(str, Enum):
  def __str__(self):
    return str(self.value)

  QUERY_DOCUMENT = 'QUERY_DOCUMENT'
  CHAT_LOGS = 'CHAT_LOGS'

def is_tab(name):
  return st.session_state['tab_name'] == name

def set_tab(name):
  st.session_state['tab_name'] = name

if 'tab_name' not in st.session_state:
  set_tab(TAB_NAMES.QUERY_DOCUMENT)

if 'chat_logs' not in st.session_state:
  st.session_state['chat_logs'] = []

if 'validation_error' not in st.session_state:
    st.session_state['validation_error'] = []


def query_sampling_click_handler():
  ## VALIDATION STEP ##
  validation_errors = []
  if ('query_str' not in st.session_state or len(st.session_state['query_str'].strip()) < 5):
    validation_errors.append('The query input is too short')
  
  st.session_state['validation_error'] = validation_errors
  if (len(validation_errors)):
    return

  # PREPARING PROMPTS
  query_prompt = get_rephrase_prompt(st.session_state['query_str'])
  st.session_state['chat_logs'].append(('user', query_prompt))

  r = get_completion_from_messages(prompt=query_prompt, api_key=st.session_state['openai_api_key'])
  st.session_state['chat_logs'].append(('assistant', r.choices[0]['text']))

  query_samples = perform_list_response(r)
  st.session_state['query_samples'] = query_samples


def query_document_click_handler():
  ## VALIDATION STEP ##
  validation_errors = []
  if ('query_samples' not in st.session_state):
    validation_errors.append('Query sampling is required')

  if ('document_str' not in st.session_state or len(st.session_state['document_str'].strip()) < 5):
    validation_errors.append('The document input is too short')
  
  st.session_state['validation_error'] = validation_errors
  if (len(validation_errors)):
    return
  
  # PREPARING PROMPTS
  query_prompt = get_document_prompt(st.session_state['query_samples'], st.session_state['document_str'])
  st.session_state['chat_logs'].append(('user', query_prompt))

  r = get_completion_from_messages(prompt=query_prompt, api_key=st.session_state['openai_api_key'])
  st.session_state['chat_logs'].append(('assistant', r.choices[0]['text']))

  answers_query_samples = perform_list_response(r)
  st.session_state['answers_query_samples'] = answers_query_samples

  most_popular_prompt = the_most_popular_prompt(answers_query_samples)
  st.session_state['chat_logs'].append(('user', most_popular_prompt))

  r = get_completion_from_messages(prompt=most_popular_prompt, api_key=st.session_state['openai_api_key'])
  st.session_state['chat_logs'].append(('assistant', r.choices[0]['text']))

  st.session_state['most_popular_prompt'] = r.choices[0]['text']


def toggle_tabs_click_handler():
  if (is_tab(TAB_NAMES.QUERY_DOCUMENT)):
    set_tab(TAB_NAMES.CHAT_LOGS)
  else:
    set_tab(TAB_NAMES.QUERY_DOCUMENT)

## STREAMLIT BODY ##

st.set_page_config(
  page_title="Self-Consistency use case", page_icon="🤖", layout="wide", initial_sidebar_state="expanded"
)

if ('openai_api_key' not in st.session_state or len(st.session_state['openai_api_key'].strip()) == 0):
  st.title("👈 Provide an OpenAI API Key")
else:
  st.title("Self-Consistency Use Case")
  st.button("Toggle tabs", on_click=toggle_tabs_click_handler)

  if is_tab(TAB_NAMES.QUERY_DOCUMENT):
    st.write("Attempt to deal with hallucinations to answer to the question with given document")

    text = st.text_area("Please Enter your query", 
                        key='query_str')

    button_value = st.button("Run a query sampling", on_click=query_sampling_click_handler)

    if 'query_samples' in st.session_state:
      messages = []
      for q in st.session_state['query_samples']:
        messages.append(q)
      st.markdown('### Sampled list of questions that will be used to request a document:')
      st.info('\n\n'.join(messages))

    if (len(st.session_state['validation_error']) > 0):
      errors = '\n\n'.join(st.session_state['validation_error'])
      st.error(errors)

    st.text_area("Please Enter the document",
                key='document_str',
                height=500)
    
    if 'query_samples' in st.session_state:
      st.button("Run a query on a document", on_click=query_document_click_handler)

    if "answers_query_samples" in st.session_state:
      messages = []
      for q in st.session_state['answers_query_samples']:
        messages.append(q)
      st.markdown('### Answers for the document:')
      st.info('\n\n'.join(messages))

      st.markdown('### Final answer:')
      st.info(st.session_state['most_popular_prompt'])

  elif is_tab(TAB_NAMES.CHAT_LOGS):
    output_container = st.empty()
    output_container = output_container.container()

    output_container.markdown('### Full LLM request history:')
    
    if (len(st.session_state['chat_logs']) > 0):
      for role, message in st.session_state['chat_logs']:
        output_container.chat_message(role).write(message)
    else:
      "No prompts"

user_openai_api_key = st.sidebar.text_input(
    "OpenAI API Key", type="password", help="Set this to run your own custom questions.", key='openai_api_key'
)