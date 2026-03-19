### Task: [Set Up & Troubleshooting]
**Prompt:** (Summary, 3 Prompts) Request assistance to ensure token is hidden on Repository, Handling error messages from token retrieval from secrets.toml. Later prompted assistance in updating repository in VS.
**AI Suggestion:** Reconfigure terminal environment, suggests code to output an error message in the event of a missing API token. Github & terminal troubleshooting 
**My Modifications & Reflections:** Modification: Removed .streamlit from chat/ folder ; Seeing that terminal errors occurred whenever .streamlit folder was inside chat/ folder. It altered the streamlit application. 


### Task: [1 - Page Set Up]
**Prompt:** (Streamlit AI, ~7 Prompts) Requesting native language around chat interface, further inquiry around specific details such as expander, divider, containers, etc.
**AI Suggestion:** (Streamlit DOC AI) Chatbot gives reference articles and direct code suggestions.
**My Modifications & Reflections:**  Modification, I implement code and iterations from the top down to create a frame for the website.Reflection: working closely with the Streamlit AI, I was able to get the functions I needed to set up an interface similar to the reference. Begin writing purposes for later function definitions with Codex


### Task: [B - Messaging]
**Prompt:** "See my code. I have run into a loop in my echo chat and misplacement of input bar. How can I adjust the ordering to maintain the structure I had before." [I am going to make my contextual API call to implement in the code, will return to this. Then will prompt for possible adjustments]
**AI Suggestion:** Codex restructures the nesting to keep prompt input at the bottom and the chat inside a scrollable container.
**My Modifications & Reflections:** Implement simple echo messaging to prepare for future API Calls. 


### Task: [C - Chat Management]
**Prompt:** (2 Prompts)"See the my set up framework for my Streamlit Sidebar, I have begun to create functions for button functionality. My "New Chat" button needs to create a New chat interface for a fresh conversation. See my "Recent Chats" portion, with its placeholder button. This button (Titled by the "Chat Title") should function to pull up the chat interface for which it is titled. ALongside, a markdown button (red "X") should give the option to delete the chat it pertains to. Create a plan for this."
(Consults Streamlit AI for nonCSS option) "Make a minor correction. Instead use this function st.button("X", type="primary") to achieve the button in the Recent Chats rows. Keep the working parts the same."
Minor error in the Sidebar, reiterate the code logic to me, because in the rows for each new chat, the date is supposeed to be in between the buttons.
**AI Suggestion:** Recommends use of chat_id for defined functions, Recent Chat Organization into rows for each. Deleting the last chat results in fresh empty chat instead of a broken UI. 
**My Modifications & Reflections:** Verifying button functions as well as JSON creation and deletion, identify respective chat history for context building. Reflect on functions to identify variables that I may need for the next step.


### Task: [D - Chat Persistence]
**Prompt:** (2 Prompts)"I have adjusted the code from echo messaging to an AI response, connected via API. In my code, the intended logic is to provide context and and ask the prompt variable. However, the response seems to be a JSON. What may be the errors here?" "Review my secondary call for API generated title, this is to replace the first sentence titling method implemented earlier. Check for errors, or rough patches."
**AI Suggestion:** Refines so data is appended & stored into active chat only, JSONs organized by chatid for mapping (prior prompt) Recommends to parse the HTTP response to extract "assistant" response. Adjustments to dual payload structure.
**My Modifications & Reflections:** I take note of each function to build context json. Editing out echo messaging logic for API call, minding token by token replies. Persistence, contextual chat, and generated titles tested, currently works.


### Task: [2 - Response Streaming]
**Prompt:** (2 Prompts)"Now, real time token by token streaming. In the primary call, I have inputted two new functions to achieve this. This may affect prior parsing logic (extract_message_content function). Further how to incorporate a short delay between rendering chunks so this effect is visible in the UI?" "The title is being erased after each run. My attempted fix has this error message on the UI *Inserted Error Message*, continual conversations need to be saved to JSON"
**AI Suggestion:** Suggests iteration over data lines for UI rendering. Subsequent appends to accumulator string for object saving. Breaks, time.sleep(0.03) between chunks. Recommends title name to be saved to JSON for reopening.
**My Modifications & Reflections:** Reflections: Verified real time chunks are outputted, non-streaming path present only for title generation. Bug causing chat output outside of container as well as Sidebar title deletion, addressed.


### Task: [3 - User Memory]
**Prompt:** "I have repurposed the title_payload function to generate a custom payload, here specifically, 'extract user's personality trait preferences'according to the memory.json categories. The api call iterates through each category the API response should give a one word response inferring the user's preference, based on user inputted prompt and then (store it as a value to the category key). The display button "Clear Memory" incorporate a native Streamlit control to clear/reset the saved memory. Ultimately, the json should be injected into the sytem prompt of future conversations, so that the model can personalize responses. Lastly, recent chats Titles keep deleting, please adjust the logic so they have persistence once generated"
Public Deployment, run error message through codex
**AI Suggestion:** Incorporates load_memory and clear_memory functions, Reviews build_special_payload def opts to separate functions, Recommends merge behavior overwrite only categories with meaningful non-empty one-word values. Model instructed to return valid JSON only
**My Modifications & Reflections:** Initial testing only adjusted memory.json upon explicit use of key words after a cleared memory. Modified API call wording for more prediction freedom. Upon attempts to upload publicly, different bugs occur. I see that much is minor failings, therefore, I adjust (Title generating, Memory.json inscripting). Final message, public deploy had discrepancies. Therefore, I recalled my last successful commit and did minor adjustments (memory payload wording) this has improved desired functions.
