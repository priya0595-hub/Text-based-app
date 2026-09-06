"""
Lecture 6 demo (Streamlit version): a text generation app built with
Semantic Kernel + Streamlit, using OpenRouter as the model provider.

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

WHY OPENROUTER INSTEAD OF OPENAI DIRECTLY
-------------------------------------------
OpenRouter (https://openrouter.ai) exposes a single, OpenAI-compatible API
in front of many different model providers, including several free models.
One API key gets you access to models from OpenAI, Anthropic, Meta, Google,
Mistral, and others, useful for comparing models (see Lecture 2) without
signing up for each provider separately.

HOW TO RUN
----------
1. Install dependencies:
     pip install -r requirements.txt

2. Create a .env file in this folder with:
     OPENROUTER_API_KEY=sk-or-v1-...
     OPENROUTER_MODEL_ID=meta-llama/llama-3.1-8b-instruct:free

   Get a free API key at https://openrouter.ai/keys. Browse available
   models, including free ones, at https://openrouter.ai/models

3. Start the app:
     streamlit run app.py

   Streamlit will open your browser automatically, usually at
   http://localhost:8501
"""

import asyncio
import os

import openai
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
#
#    OpenRouter (https://openrouter.ai) exposes an OpenAI-compatible API,
#    so we reuse Semantic Kernel's OpenAIChatCompletion connector, we just
#    point it at OpenRouter's endpoint and use an OpenRouter API key and
#    model name instead of OpenAI's directly. Semantic Kernel doesn't take
#    a base_url argument itself, so we build our own AsyncOpenAI client
#    with that base_url and hand it in via async_client.
# ---------------------------------------------------------------------------
@st.cache_resource
def get_kernel() -> Kernel:
    async_client = openai.AsyncOpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )
    kernel = Kernel()
    kernel.add_service(
        OpenAIChatCompletion(
            service_id="storyteller",
            ai_model_id=os.getenv(
                "OPENROUTER_MODEL_ID", "meta-llama/llama-3.1-8b-instruct:free"
            ),
            async_client=async_client,
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
                # Semantic Kernel wraps the real error from the OpenAI client
                # several levels deep in __cause__. Walk to the bottom of the
                # chain, since that innermost exception usually names the
                # actual problem (bad key, no quota, bad model name, network
                # block, etc.) far more clearly than the outer wrapper does.
                root_cause = exc
                while root_cause.__cause__ is not None:
                    root_cause = root_cause.__cause__

                story = (
                    "Something went wrong while generating your story.\n\n"
                    f"**Error type:** `{type(root_cause).__name__}`\n\n"
                    f"**Details:** {root_cause}\n\n"
                    "Common causes: an incorrect or expired OPENROUTER_API_KEY, "
                    "no remaining free credits on your OpenRouter account, "
                    "a model ID that doesn't exist or isn't free/available to "
                    "you, or a network/firewall block. Full traceback is also "
                    "in your terminal. Check available model IDs at "
                    "https://openrouter.ai/models"
                )
        st.markdown(story)

    st.session_state.messages.append({"role": "assistant", "content": story})
