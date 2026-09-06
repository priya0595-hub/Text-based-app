"""
Lecture 6 demo (Streamlit version): a text generation app built with
Semantic Kernel + Streamlit.

WHY STREAMLIT INSTEAD OF CHAINLIT
----------------------------------
As of this writing, Chainlit (and other Starlette/anyio-based frameworks)
crash on Python 3.14 with a "NoEventLoopError" while serving static files.
This is an upstream bug in how anyio detects the running event loop on
Python 3.14, unrelated to this app's code, and it is not yet fixed.

Streamlit runs on a different foundation (Tornado, not Starlette/anyio),
so it does not hit this bug. This file keeps the same Semantic Kernel
logic from the Chainlit version, only the UI layer has changed. It uses
Streamlit's chat components (st.chat_message, st.chat_input) so it still
feels like a conversational app rather than a plain form.

HOW TO RUN
----------
1. Install dependencies:
     pip install -r requirements.txt

2. Create a .env file in this folder with:
     OPENAI_API_KEY=sk-...
     OPENAI_CHAT_MODEL_ID=gpt-4o-mini

3. Start the app:
     streamlit run app.py

   Streamlit will open your browser automatically, usually at
   http://localhost:8501
"""

import asyncio
import os

import streamlit as st
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments, KernelFunctionFromPrompt

# ---------------------------------------------------------------------------
# 0. Load environment variables from .env (Streamlit does not do this
#    automatically, unlike Chainlit's CLI).
# ---------------------------------------------------------------------------
load_dotenv()

st.set_page_config(page_title="Story Generator", page_icon="📖")

# ---------------------------------------------------------------------------
# 1. Set up the Kernel once per session and cache it, so we don't rebuild
#    the connection on every rerun (Streamlit reruns the whole script on
#    every interaction).
# ---------------------------------------------------------------------------
@st.cache_resource
def get_kernel() -> Kernel:
    kernel = Kernel()
    kernel.add_service(
        OpenAIChatCompletion(
            service_id="storyteller",
            ai_model_id=os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4o-mini"),
        )
    )
    return kernel


kernel = get_kernel()

# ---------------------------------------------------------------------------
# 2. The same reusable prompt template from the Chainlit version.
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """
Write a short, {{$style}} story about: {{$topic}}
Keep it under 150 words.
"""


async def generate_story(topic: str, style: str, temperature: float, max_tokens: int) -> str:
    """Builds the semantic function fresh (so it picks up current slider
    values) and asks the model to run it."""
    exec_settings = kernel.get_prompt_execution_settings_from_service_id("storyteller")
    exec_settings.temperature = temperature
    exec_settings.max_tokens = max_tokens

    story_function = KernelFunctionFromPrompt(
        function_name="write_story",
        plugin_name="storyteller_plugin",
        prompt=PROMPT_TEMPLATE,
        prompt_execution_settings=exec_settings,
    )

    result = await kernel.invoke(
        story_function,
        arguments=KernelArguments(topic=topic, style=style),
    )
    return str(result)


# ---------------------------------------------------------------------------
# 3. Sidebar settings, equivalent to Chainlit's ChatSettings sliders.
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    style = st.selectbox(
        "Story style",
        ["whimsical", "dramatic", "comedic", "mysterious", "poetic"],
        index=0,
    )
    temperature = st.slider("Creativity (temperature)", 0.0, 1.5, 0.8, 0.1)
    max_tokens = st.slider("Max length (tokens)", 100, 800, 400, 50)
    st.caption("Change these, then send a new topic to see the effect.")

# ---------------------------------------------------------------------------
# 4. Chat-style interface using Streamlit's chat components.
# ---------------------------------------------------------------------------
st.title("📖 Story Generator")
st.caption("Built with Semantic Kernel + Streamlit")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                "Type a topic, for example **a robot learning to paint**, "
                "and I'll write you a short story about it. Use the sidebar "
                "to change the style, creativity, and length."
            ),
        }
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

topic = st.chat_input("Enter a story topic...")

if topic:
    st.session_state.messages.append({"role": "user", "content": topic})
    with st.chat_message("user"):
        st.markdown(topic)

    with st.chat_message("assistant"):
        with st.spinner("Writing your story..."):
            try:
                story = asyncio.run(
                    generate_story(topic, style, temperature, max_tokens)
                )
            except Exception as exc:  # noqa: BLE001 - shown to the user for a classroom demo
                story = (
                    "Something went wrong while generating your story.\n\n"
                    f"Details: {exc}\n\n"
                    "Check that your OPENAI_API_KEY is set correctly in your .env file."
                )
        st.markdown(story)

    st.session_state.messages.append({"role": "assistant", "content": story})
