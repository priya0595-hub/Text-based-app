# Story Generator (Semantic Kernel + Streamlit + OpenRouter)

A short-story generator built for **Lecture 6: Building Text Generation
Applications**. **Semantic Kernel** handles the AI logic (the prompt
template, the model connection, temperature/token settings), **Streamlit**
provides a chat-style interface using `st.chat_message` and `st.chat_input`,
and **OpenRouter** provides the model, giving access to many providers
(OpenAI, Anthropic, Meta, Google, Mistral, and more) through one API key,
including free models.

## Why Streamlit (and not Chainlit)?

This app was originally built with Chainlit. On **Python 3.14**, Chainlit
(and other frameworks built on Starlette + anyio) currently crash with an
`anyio.NoEventLoopError` while serving static files, an unresolved upstream
bug unrelated to this app's code (tracked as
[Chainlit issue #2767](https://github.com/Chainlit/chainlit/issues/2767)).

Streamlit runs on a different foundation (Tornado, not Starlette/anyio), so
it does not hit this bug. This version works on Python 3.14 with no need to
install an older Python version.

## Why OpenRouter (and not OpenAI directly)?

OpenRouter (<https://openrouter.ai>) exposes a single, OpenAI-compatible API
in front of many model providers. Benefits for this course:

- **Free models available**, no billing setup required to get started.
- **One key, many providers**, useful for comparing models the way
  Lecture 2 discusses, without signing up separately for OpenAI,
  Anthropic, Google, etc.
- Semantic Kernel's `OpenAIChatCompletion` connector works with it directly,
  we just point it at OpenRouter's endpoint instead of OpenAI's.

## What it does

Type a topic, such as `a robot learning to paint`, into the chat box, and
the app writes a short story about it. You can change the story's style,
creativity (temperature), and length any time from the sidebar, changes
apply to your next message.

## Setup

1. **Install Python 3.10 or newer** (this works fine on the latest version,
   including 3.14). Create a virtual environment (recommended but not
   required):

   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```

2. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Get a free OpenRouter API key** at <https://openrouter.ai/keys>
   (sign up if you don't have an account yet).

4. **Add your API key.** Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   On Windows PowerShell, if `cp` isn't recognized, use:

   ```powershell
   Copy-Item .env.example .env
   ```

   Then open `.env` and replace `sk-or-v1-your-key-here` with your real
   OpenRouter key.

   **Never paste your real API key into a chat, email, or public
   repository.** If a key is ever exposed, delete it on the OpenRouter
   dashboard and generate a new one right away.

5. **Run the app:**

   ```bash
   streamlit run app.py
   ```

   Streamlit opens automatically in your browser, usually at
   <http://localhost:8501>.

## Choosing a model

The default, `openrouter/free`, is a router that automatically selects a
currently-available free model for you, this is deliberately robust,
since specific free model slugs get retired or rate-limited over time
(this happened during testing: `meta-llama/llama-3.1-8b-instruct:free`
stopped being free shortly after this app was built).

If you want consistent, repeatable output for a demo (the same model every
time, rather than whatever the router picks), browse specific free models
at <https://openrouter.ai/models> (filter by "Free" in the pricing filter)
and set `OPENROUTER_MODEL_ID` in your `.env` to that exact slug instead.
Check the page right before class, free model availability changes.

## Files in this folder

| File               | Purpose                                             |
|--------------------|------------------------------------------------------|
| `app.py`           | The application code (Semantic Kernel + Streamlit)  |
| `requirements.txt` | Python packages needed to run the app               |
| `.env.example`     | Template for your API key; copy it to `.env`        |
| `README.md`        | This file                                           |

## Trying it out

- Send different topics and compare styles (whimsical vs. dramatic vs. mysterious).
- Raise the "Creativity" slider toward 1.5 and send the same topic again,
  compare it against a low-temperature run, the nondeterminism discussed
  in Lecture 5.
- Lower "Max length" to something small (e.g. 100) and notice the story
  gets cut off mid-sentence, a live example of the token-limit issue
  covered in Lecture 6.
- Swap `OPENROUTER_MODEL_ID` for a different free model and compare the
  same topic across models, a hands-on version of Lecture 2.

## Troubleshooting

**`ModuleNotFoundError` for `streamlit`, `semantic_kernel`, or `openai`:**
Your virtual environment probably isn't active, or the dependencies
weren't installed into it. Confirm your terminal prompt shows `(venv)`,
then rerun `pip install -r requirements.txt`.

**An error message appears in the chat after you send a topic:**
`app.py` unwraps Semantic Kernel's error chain and shows you the real,
underlying error type and message directly in the chat, for example
`AuthenticationError` (bad key), or a message about an invalid model ID.
Read that message first, it usually names the exact problem.

**`streamlit` command not recognized:**
Same fix as before, run it as a module instead:
```bash
python -m streamlit run app.py
```

## Extending it (optional, for the in-class activity)

To turn this into the product-description writer or study-notes
summarizer from the in-class activity, you mainly need to change:

1. `PROMPT_TEMPLATE`, to match the new task.
2. The `KernelArguments(...)` passed in `generate_story()` (rename the
   function too, if you like).
3. The welcome message text and page title.

The Semantic Kernel, Streamlit, and OpenRouter wiring around it stays the
same.
