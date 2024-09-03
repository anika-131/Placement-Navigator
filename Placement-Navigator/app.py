import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
from dataclasses import dataclass
import pypdf
from typing import Literal
import streamlit.components.v1 as components



openai.api_key = "apiKey"



# Set custom theme colors
st.set_page_config(
    page_title="Ask away",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None
)
st.title("Chat with PESU placements 💬💼")
# Load data using llamaindex
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Your University docs - hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./Data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(
            llm=OpenAI(
                model="gpt-3.5-turbo",
                temperature=0.2,
                system_prompt="You have the placement data for 3 years of PES University. Assume all input prompts to be with respect to the input data. Answer all placement and company related queries"
            )
        )
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()
import re

def extract_year_from_query(query):
    # Use a regular expression to find a year pattern in the query
    year_pattern = r'\b\d{4}\b'  # Assumes that the year is a 4-digit number
    match = re.search(year_pattern, query)
    
    if match:
        return match.group()
    else:
        return None

class Conversation:
    def _init_(self):
        # Your initialization logic here
        self.memory = {}  
        self.year = None

    def setup(self):
        # Your setup logic here
        pass

    def update_year(self, year):
        self.year = year

def initialize_conversation():
    # Your code to set up and return the conversation object
    conversation = Conversation()
    conversation.setup()
    return conversation
# Initialize chat engine
chat_engine = index.as_chat_engine(verbose=True)
# Initialize chat messages history and other attributes
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "I can help you with your University Placements stats 📊"}
    ]
    st.session_state.history = []  # Initialize history attribute
    st.session_state.token_count = 0  # Initialize token_count attribute
    if "conversation" not in st.session_state.keys() or st.session_state.conversation is None:
        st.session_state.conversation = initialize_conversation()


# Apply styles to the prompt using st.markdown
chat_form_style = """
    <style>
        body {
            background-image: url('/images/int.jpg'); 
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }

        .stForm {
            background-color: rgba(255, 255, 255, 0.8); /* Set a background color with opacity */
            padding: 20px;
            border-radius: 10px;
        }
    </style>
"""
st.markdown(chat_form_style, unsafe_allow_html=True)

# Display the radio button to select placement info year
radio = st.radio("Select the placement information year", options=["2021", "2022", "2023"])  # to get radio button input from the user
toggle = st.toggle("For more information on internship ") # to get toggle input from the user
st.write(radio)

response = None  # Initialize response variable

with st.form("chat-form"):
    prompt = st.text_input(
        'Ask me a question about job opportunities or career advice 🎓',
        key="human_prompt",
    )
    if st.form_submit_button("Submit", type="primary"):
        # Append user message to history
        st.session_state.messages.append({"role": "user", "content": prompt, "year": radio})

        # Check if the selected year is different from the year mentioned in the user's query
        user_query_year = extract_year_from_query(prompt)
        if user_query_year and user_query_year != radio:
            st.warning(f"The selected year ({radio}) is different from the year mentioned in your query ({user_query_year}).")

        # Update the conversation with the selected year
        st.session_state.conversation.update_year(radio)

        # Generate response if needed
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)

            # Append assistant message to history
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)

# # Area chart based on user input
# if response:
#     response_text = response.response
#     st.write("Chatbot Response:", response_text)  # Debugging statement

#     data_from_chatbot = [int(x) for x in response_text.split() if x.isdigit()]
#     st.write("Extracted data from chatbot:", data_from_chatbot)  # Debugging statement

#     st.area_chart(data_from_chatbot)

# Display chat history
for message in reversed(st.session_state.messages):
    with st.container():
        st.image("travel-agency.png" if message["role"] == "user" else "chatbot.png", width=50)
        st.write(message["content"])




# # Add a toggle button to show/hide the sidebar
# toggle_sidebar = st.sidebar.checkbox("Toggle Sidebar", True)

# # Check the toggle value
# if toggle_sidebar:
#     with st.sidebar:
#         st.markdown("Placement companies menu:")
#         st.caption("This is a sidebar caption")
internship_companies = [
    "Altair Engineering India Pvt Ltd",
    "Aruba-HPE",
    "Ather Energy Pvt. Ltd.",
    "Autoliv India Pvt. Ltd",
    "Clay works",
    "Delta X Automotive Pvt Ltd",
    "Drongo AI",
    "Elegant Builders and Promoters",
    "Flipkart",
    "Goldman Sachs (Operation)",
    "HevoData",
    "Hewlett Packard Enterprise (GBO)",
    "Hewlett Packard Enterprise (R&D)",
 
]

if toggle:
   with st.sidebar:
        st.image("/images/int.jpg", width=225, caption=" ")
        st.markdown("## Internship Companies ")
        st.caption("To name a few 🔍:  ")
        for company in internship_companies:
            st.write(f"- {company}")
        st.write('For more details and questions asked in the interviews, ask the chatbot')


else:
    st.write(" ")