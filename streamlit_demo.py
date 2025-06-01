import os
import asyncio
import streamlit as st
import langgraph_agent as la
from langchain_core.messages import AIMessage


# Initialize streamlit web UI
st.markdown("<h1 style='text-align: center;'>DiningAI Demo Web 🍃</h1>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)


image_uploader = st.file_uploader(label="image",  type=["jpeg"])
go_button = st.button("Analyze Image", type="primary")

# Create containers for streaming output
analysis_container = st.empty()
query_container = st.empty()

async def process_stream(image_path):
    analysis_text = ""
    query_text = ""
    
    async for chunk in la.dining_ai(image_path):
        print("chunk: ", chunk)
        analysis_messages = chunk.get('analysis', {}).get('messages', [])
        query_messages = chunk.get('query', {}).get('messages', [])

        # Update analysis messages
        if analysis_messages:
            last_message = analysis_messages[-1]
            if isinstance(last_message, AIMessage):
                content = getattr(last_message, 'content', None)
                if isinstance(content, str):
                    analysis_text += content + "\n\n"
                analysis_container.markdown("### Analysis Agent🧑‍🍳:\n" + analysis_text)

        # Update query messages
        if query_messages:
            last_message = query_messages[-1]
            if isinstance(last_message, AIMessage):
                content = getattr(last_message, 'content', None)
                if content:
                    if isinstance(content, str):
                        query_text += str(content) + "\n\n"
                    query_container.markdown("### Query Agent🧑‍💻:\n" + query_text)

# Call agent to use tools
if go_button:
    if image_uploader is not None:
        image_path = os.path.join("image", image_uploader.name)
        with open(image_path, "wb") as f:
            f.write(image_uploader.getbuffer())
            
        with st.spinner("Working..."):
            asyncio.run(process_stream(image_path))
    else:
        st.write("Upload an image!")





