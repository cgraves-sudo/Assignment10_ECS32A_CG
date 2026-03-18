### Task: [Task Name]
**Prompt:** "[Paste your prompt here or summarize if too long]"
**AI Suggestion:** [Brief summary of what the AI suggested]
**My Modifications & Reflections:** [Did the code work? Did you adapt anything to fit the assignment?]

### Task: [Set Up & Troubleshooting]
**Prompt:** (Summary, 3 Prompts) Request assistance to ensure token is hidden on Repository, Handling error messages from token retrieval from secrets.toml. Later prompted assistance in updating repository in VS.
**AI Suggestion:** Reconfigure terminal environment, suggests code to output an error message in the event of a missing API token. Github & terminal troubleshooting 
**My Modifications & Reflections:** Modification: Removed .streamlit from chat/ folder ; Seeing that terminal errors occurred whenever .streamlit folder was inside chat/ folder. It altered the streamlit application. 

### Task: [1 - Page Set Up]
**Prompt:** (Streamlit AI, ~7 Prompts) Requesting native language around chat interface, further inquiry around specific details such as expander, divider, containers, etc.
**AI Suggestion:** (Streamlit DOC AI) Chatbot gives reference articles and direct code suggestions.
**My Modifications & Reflections:**  Modification, I implement code and iterations from the top down to create a frame for the website.Reflection: working closely with the Streamlit AI, I was able to get the functions I needed to set up an interface similar to the reference. Begin writing purposes for later function definitions with Codex

### Task: [B - Messaging]
**Prompt:** (Summary, TBA Prompts) "See my code. I have run into a loop in my echo chat and misplacement of input bar. How can I adjust the ordering to maintain the structure I had before." [I am going to make my contextual API call to implement in the code, will return to this. Then will prompt for possible adjustments]
**AI Suggestion:** Codex restructures the nesting to keep prompt input at the bottom and the chat inside a scrollable container.
**My Modifications & Reflections:** Implement simple echo messaging to prepare for future API Calls. 

### Task: [C - Chat Management]
**Prompt:** (2 Prompts)"See the my set up framework for my Streamlit Sidebar, I have begun to create functions for button functionality. My "New Chat" button needs to create a New chat interface for a fresh conversation. See my "Recent Chats" portion, with its placeholder button. This button (Titled by the "Chat Title") should function to pull up the chat interface for which it is titled. ALongside, a markdown button (red "X") should give the option to delete the chat it pertains to. Create a plan for this."
(Consults Streamlit AI for nonCSS option) "Make a minor correction. Instead use this function st.button("X", type="primary") to achieve the button in the Recent Chats rows. Keep the working parts the same."
Minor error in the Sidebar, reiterate the code logic to me, because in the rows for each new chat, the date is supposeed to be in between the buttons.
**AI Suggestion:** Recommends use of chat_id for defined functions, Recent Chat Organization into rows for each. Deleting the last chat results in fresh empty chat instead of a broken UI. 
**My Modifications & Reflections:** Verifying button functions as well as JSON creation and deletion, identify respective chat history for context building. Reflect on functions to identify variables that I may need for the next step.


### Task: [D - Chat Persistence]
**Prompt:** 
**AI Suggestion:** Refines so data is appended & stored into active chat only, JSONs organized by chatid for mapping (prior prompt)
**My Modifications & Reflections:** I take note of each function to build context json

### Task: []
**Prompt:** 
**AI Suggestion:** 
**My Modifications & Reflections:** 

### Task: []
**Prompt:** 
**AI Suggestion:** 
**My Modifications & Reflections:** 

### Task: []
**Prompt:** 
**AI Suggestion:** 
**My Modifications & Reflections:** 
