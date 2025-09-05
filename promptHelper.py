import streamlit as st
import json
import pyperclip as pc
from google import genai

#from secrets import secrets

#TODO 
# Fix secrets
# implement Clear button
# implement chunking on text outputs
#

@st.cache_resource
def initAI():
	#googleapikey = secrets.secrets('GOOGLE_API_KEY')
	googleapikey ="AIzaSyBC6tI_A5paMPTTAJt9OU1V25Ussf9iCeo"
	global client
	client = genai.Client(api_key=googleapikey)	
	return client

@st.cache_data
def loadPrompts(path):
	# Open and read the JSON file
	with open(path, 'r') as promptsfile:
		promptlist = json.load(promptsfile)
	promptsfile.close()
	return promptlist

def clipCopy():
	pc.copy(str(st.session_state['newPrompt']))

def clearPrompt():
	st.session_state['currentPrompt'] = ''

@st.cache_data
def getFileNames():
	filenames = ["Clip_01", "Clip_02", "Clip_03", "Clip_04", "Clip_05", "Clip_06"]
	return filenames

@st.cache_resource
def doPromptEval(prompttext):
	evaltext = "The following is prompt to a Video-Capable Language Model that is inteded to produce and accurate, descriptive, formal and understandable output. Provide an evaluation of how effective this prompt would be. The content of the videos being analysed may include people, multiple vehicles, signs, signalling, roads, walkways, public infrastructure, buildings, animals and many other factors. The prompt should provide a response rich in detailed information along many dimensions, including time-dependent factors."
	evalsuffix = " Keep the response terse and to-the-point. Do not provide suggestions for changes."
	llmprompt= evalsuffix+evaltext+prompttext
	global response
	response = client.models.generate_content(
    model="gemini-2.0-flash", contents=llmprompt)
	return response.text

@st.cache_resource
def doNewPrompt(prompttext, responsetext, struct, sum, env):
	evaltext = "The following is prompt to a Video-Capable Language Model that is inteded to produce and accurate, descriptive, formal and understandable output."
	newpromptVerbosity = " Produce an output that is designed to be input into a Video Langauge Model, capable of analysing video. Keep the response terse and to-the-point. Do not provide suggestions for changes. Preface the text with instructions to analyse a video segment."
	newpromptEval = "The following is an evaluation of the prompt. Provide a new and better prompt that will generate a better and more accurate output. "
	if struct:
		newpromptStructure =  "Provide numbered, stepwise instructions for each dimension or domain to be explored. Suggest constrained outputs such as numbers, short summaries or files." 
	else:
		newpromptStructure = "Provide a natural description of the instructions, designed to produce an output that is easy to understand and readable. Do not suggest filetype outputs, suggest the use of words instead of numbers. "

	if env:
		newPromptEnv = "Include queries about the general environment, such as weather, buildings, infrastructure, biosphere, people etc."
	else:
		newPromptEnv = "Focus on the elements included in the original prompt, do not unclude potentially unrelated environmental factors."
	llmprompt= newpromptVerbosity+newpromptStructure+newPromptEnv+evaltext+prompttext+ newpromptEval+ responsetext
	global newresponse
	newresponse = client.models.generate_content(
    model="gemini-2.0-flash", contents=llmprompt)
	return newresponse.text

def prompt_change():
	#print(st.session_state["prompt_box"])
	#st.session_state['currentPrompt']
	pass

# Set session variables
if 'LLMEval' not in st.session_state:
	st.session_state['LLMEval'] = ''

if 'currentPrompt' not in st.session_state:
	st.session_state['currentPrompt'] = ''

if 'currentPromptSel' not in st.session_state:
	st.session_state['currentPromptSel'] = ''

if 'newPrompt' not in st.session_state:
	st.session_state['newPrompt'] = ''


client = initAI()
 
# list available models
eval_models = ["GPT-5", "Claude", "Gemini"]

lorem = "THIS IS THE VLM RESPONSE!"
# Open and read the JSON file

promptlist=loadPrompts('assets/Prompts.json')
# Get prompt DisplayNames into list for menus
promptnames = [] 
for prompt in promptlist:
	promptnames.append(prompt['DisplayName'])



# Start GUI

title = st.title("PromptHelper")
# VLM Section
with st.container(border=True):
	clipnames = getFileNames()
	st.header("VLM Clips Sandbox")
	st.text("Select a Prompt from the library, or create your own and save it.")
	prompt_selection = st.selectbox("Prompt Library", promptnames, key="prompt_box", on_change = prompt_change)

	for prompt in promptlist:
		if prompt['DisplayName'] == prompt_selection:
			promptcontent = prompt['Prompt']
			if promptcontent:
				st.session_state['currentPrompt'] = promptcontent
			

	prompt_text = st.text_area("Enter your prompt for evaluation", value=st.session_state['currentPrompt'], height="content")

	if prompt_text:
		st.session_state['currentPrompt'] = prompt_text

	col11, col12, col13 = st.columns([1,1,1],vertical_alignment="bottom")
	with col11:
		clear_button = st.button("Clear Prompt Text", width="stretch", on_click=clearPrompt)
	with col12:
		save_prompt_button = st.button("Save Prompt As...", width="stretch")
	with col13:
		save_prompt_button = st.button("Overwrite Prompt", width="stretch")

	col1,col2 = st.columns([1,2], vertical_alignment="top")
	with col1: 
		clip_selection = st.selectbox("Select Clip", clipnames)

	with col2:
		st.image('assets/traffic.jfif', width="stretch")	

	send_to_vlm_button = st.button("Send Clip and Prompt to VLM", width="stretch")

	if(send_to_vlm_button):
		st.text_area("VLM Output", value=lorem, height="content")

# LLM Prompt Evaluation Section
with st.container(border=True):
	st.header("Prompt Assistant")
	col1, col2 = st.columns([1,1],vertical_alignment="bottom")
	with col1:
		model_selection = st.selectbox("Model", eval_models)
	with col2:	
		submit_button = st.button("Evaluate Prompt", width="stretch")

	if(submit_button):
		LLMEval = doPromptEval(st.session_state['currentPrompt'])
		if LLMEval:
			st.session_state['LLMEval'] = LLMEval

	try:
		st.text_area("Evaluation", value=st.session_state['LLMEval'], height="content")
		chatprompt = st.chat_input(placeholder="Ask about the prompt", width="stretch")
	except NameError:
		pass
	col1, col2, col3 = st.columns([1,1,1],vertical_alignment="bottom")
	with col1:
		structure_output = st.checkbox("Ask for Structured Output")
	with col2:
		summary_output = st.checkbox("Ask for Summarized Output")
	with col3:
		environment_output = st.checkbox("Include Environment")



	make_new_prompt_button = st.button("Generate New Prompt", width="stretch")
	if (make_new_prompt_button):
		newptext=doNewPrompt(st.session_state['currentPrompt'], st.session_state['LLMEval'], structure_output, summary_output, environment_output)
		if(newptext):
			st.session_state['newPrompt'] = newptext
		st.text_area("Suggested New Prompt", value= st.session_state['newPrompt'], height="content")
		copy_button = st.button("Copy to Clipboard", width="stretch", on_click=clipCopy)

