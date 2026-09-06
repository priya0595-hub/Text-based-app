# Story Generator (Semantic Kernel + Streamlit)

A short-story generator built for **Lecture 6: Building Text Generation
Applications**. **Semantic Kernel** handles the AI logic (the prompt
template, the model connection, temperature/token settings), and
**Streamlit** provides a chat-style interface, using `st.chat_message` and
`st.chat_input` so it feels like a real conversational app, not just a form.

## Why Streamlit (and not Chainlit)?

This app was originally built with Chainlit. On **Python 3.14**, Chainlit
(and other frameworks built on Starlette + anyio) currently crash with an
`anyio.NoEventLoopError` while serving static files, an unresolved upstream
bug unrelated to this app's code (tracked as
[Chainlit issue #2767](https://github.com/Chainlit/chainlit/issues/2767)).

Streamlit runs on a different foundation (Tornado, not Starlette/anyio), so
it does not hit this bug. This version works on Python 3.14 with no need to
install an older Python version.

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

3. **Add your API key.** Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   On Windows PowerShell, if `cp` isn't recognized, use:

   ```powershell
   Copy-Item .env.example .env
   ```

   Then open `.env` and replace `sk-your-key-here` with a real key from
   <https://platform.openai.com/account/api-keys>.

   **Never paste your real API key into a chat, email, or public
   repository.** If a key is ever exposed, delete it on the OpenAI
   dashboard and generate a new one right away.

4. **Run the app:**

   ```bash
   streamlit run app.py
   ```

   Streamlit opens automatically in your browser, usually at
   <http://localhost:8501>.

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

## Troubleshooting

**`ModuleNotFoundError` for `streamlit` or `semantic_kernel`:**
Your virtual environment probably isn't active, or the dependencies
weren't installed into it. Confirm your terminal prompt shows `(venv)`,
then rerun `pip install -r requirements.txt`.

**Nothing happens after you send a topic, or you see an error message
inline in the chat:**
Check that `OPENAI_API_KEY` in your `.env` file is correct and that the
file is in the same folder as `app.py`. `app.py` catches errors from the
model call and shows them directly in the chat, so the error message
itself usually tells you what's wrong.

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

The Semantic Kernel and Streamlit wiring around it stays the same.
