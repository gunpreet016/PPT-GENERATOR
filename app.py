# Step 1:Load modules
import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st
#============Step 2: Streamlit Front-end=========
# To show web-app: complete page layout
st.set_page_config(layout="wide")

st.title("AI PPT GENERATOR")
st.divider()
st.sidebar.title("Enter API-KEYS")

#============Step 3: Load API Keys=============
GOOGLE_API_KEY = st.sidebar.text_input("GOOGLE_API", type = "password")
TAVILY_API_KEY = st.sidebar.text_input("TAVILY_API", type = "password")

#==========API VALIDATIONS============
ALL_API = [GOOGLE_API_KEY,TAVILY_API_KEY]

if not all(ALL_API):
  st.sidebar.error("MUST PASS ALL API-KEYS")
elif all(ALL_API):
  st.sidebar.success("API-KEYS LOADED SUCCESSFULLY")
  # MODEL LOAD
  model = ChatGoogleGenerativeAI(
    google_api_key = GOOGLE_API_KEY,
    model = st.sidebar.selectbox("Gemini-Model-Name",
                                 options = ["gemini-2.5-flash",
                                            "gemini-2.5-flash-lite",
                                            "gemini-3.5-flash",
                                            "gemini-2.5-flash-lite"])
  )
else:
  st.sidebar.info("CHECK_API_KEYS")

#================Step 5: Backend code=====================
# Search_latest_info using tavily
def search_latest_info(query):
  """This function helps to give
  latest search using tavily
  based on given user query related research or contents"""

  client = TavilyClient(api_key = TAVILY_API_KEY)
  response = client.search(query)
  return response

#====================Step 6: User Input=========================
st.sidebar("Write Prompt to Generate PPT or Image or Fetch Latest News")

user_input = st.text_area("Write Here: ")

#TOOL 2: GENERATE IMAGE USING FREE API

def generate_image(img_prompt, slide_no = 1):
  """This function  helps user to generate
  image using free api,  with given
  img_prompt"""

  url = f"https://image.pollinations.ai/{img_prompt}"

  import requests as r
  content = r.get(url).content
  with open(f"ai_image_{slide_no}.jpeg", 'wb') as f:
    f.write(content)

  from PIL import Image
  img = Image.open(f"ai_image_{slide_no}.jpeg")
  return url

def agent_prompt(query):
  """This help to promptify the given user
  query, suppose user needs PPT based on given
  query by user, it give detailed Professional prompt
  to return the output"""

  prompt = f"""Give detailed highly professional
  prompt for below given prompt.

  you are a professional ppt designer,
  based on user given query, your task is to professional
  HTML output prompt with no markdowns.
  User Query: {query}"""

  response = model.invoke(prompt)
  final_prompt = response.content[-1]['text']

  with open("PPT_PROMPT.txt", 'w') as f:
    f.write(final_prompt)

  return final_prompt

def run_agent(leader_agent,query):
  prompt = f"""Based on Below given Query,
  your task is to call specific tool, first to
  promptify use prompt, than call image tool,or
  latest serach if required give slide dynamic,ui ux,
  with creative design, keep help function to generate image
  and embed or use direct url based on given topic,
  Generate image using
  with no of slide asked
  and imbed that in same html ppt
  and using file handling embed this in output html, use java script function
  to generate image using async func and threading and give output in HTML
  user query given below:
  """

  prompt = agent_prompt(prompt+query)
  # prompt = agent_prompt(prompt)


  response = leader_agent.invoke({'messages':[{'role':'user','content':prompt}]})
  code = response['messages'][-1].content[-1]['text']
  return code


#=====================Step 7: Agent call==========================
# leader_agent creation
if all(ALL_API):
  leader_agent = create_agent(
    model = model,
    tools = [search_latest_info,
             generate_image]
)
else:
  st.info("Pass-ALL-API-KEYS and Rerun")
#===================Step 8:Navar Streamlit=========================
tab1,tab2,tab3 = st.tabs(["Generate Image",
                          "Fetcg Latest News",
                          "Generate PPT"])


if (user input) and (leader_agent):
  # TAB 1 CODE :
  with tab2:
    if st.button("Generate Image",key ="Gen-Image"):
      with st.spinner("Running agent"):
        try:
          img = generate_image(user_input)
          st.image(url)
        except:
          url = f"https://image.pollinations.ai/{user_input}"
          time.sleep(4)
          st.image(url)
#TAB 2 CODE:
with tab2:
  if st.button("Fetch News", key = "Fetch-News"):
    with st.spinner("Running Agent"):
      try:
        prompt = "Give Multiple News in HTML Card Format for topic" + User_input
        response = leader_agent.invoke({'messages':[{'role':'user',
                                                     'content':prompt}]})
        code = response['messages'][-1].content[-1] ['text']
        st.html(code, width="stretch",
                unsafe_allow_javascript=True)
      except Exception as err:
        st.error(err)
# TAB 3 Code:
with tab3:
  if st.button("Generate PPT", key = "Gen-PPT"):
    with st.spinner("Running Agent"):
      try:
        code = run_agent(leader_agent, user_input)
        st.html(code, width="stretch",
                unsafe_allow_javascript=True)
        # File save
        with open("ppt.html", 'w') as f:
          f.write(code)
        st.download_button (label = "DOWNLOAD PPT",
                            data = code,
                            file_name = 'ppt.html',
                            mime = 'text/html')
        except Exception as err:
          st.error(err)
