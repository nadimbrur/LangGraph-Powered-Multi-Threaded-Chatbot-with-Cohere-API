import streamlit as st
from langgraph_database_backend import chatbot, retrive_all_threads
from langchain_core.messages import HumanMessage
import uuid

#*******************utility function****************************88

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    st.session_state['thread_id'] = generate_thread_id()
    st.session_state['message_history'] = []
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    # return chatbot.get_state(config={'configurable':{'thread_id': thread_id}}.values['messages'])
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}})

#***********************Session setup*******************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrive_all_threads()

add_thread(st.session_state['thread_id'])


#***********************Side bar UI*******************

st.sidebar.title('Lang Graph Chat bar')

if st.sidebar.button('New chat'):
    reset_chat()
    
    

st.sidebar.button('My conversation')

flag = 1
for i, element in enumerate(st.session_state['chat_threads'][::-1]):

    state_info = load_conversation(element).values

    if len(state_info) == 0:
        if flag:
            st.sidebar.button(str('Name is loading!..'))
            flag=0
        else:
            st.session_state['chat_threads'].remove(element)

    else:
        total_messages = state_info['messages']
        if st.sidebar.button(str(total_messages[0].content[:10])+ " ....." ):
            st.session_state['thread_id'] = element
            tmp_messages = []
            for msg in total_messages:
                if isinstance(msg, HumanMessage):
                    role = 'user'
                else:
                    role = 'assistant'
                tmp_messages.append({'role':role, 'content':msg.content})
            
            st.session_state['message_history'] = tmp_messages
    






#***********************Main UI*******************

for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.text(msg['content'])


user_input = st.chat_input('Type here')

if user_input:
      
    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)


    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}


    with st.chat_message('assistant'):
        # st.text(ai_message)
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages')  
        )
        st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})