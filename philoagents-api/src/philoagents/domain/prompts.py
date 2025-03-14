import opik
from loguru import logger


class Prompt:
    def __init__(self, name: str, prompt: str) -> None:
        self.name = name

        try:
            self.__prompt = opik.Prompt(name=name, prompt=prompt)
        except Exception:
            logger.warning(
                "Can't use Opik to version the prompt (probably due to missing or invalid credentials). Falling back to local prompt. The prompt is not versioned, but it's still usable."
            )

            self.__prompt = prompt

    @property
    def prompt(self) -> str:
        if isinstance(self.__prompt, opik.Prompt):
            return self.__prompt.prompt
        else:
            return self.__prompt

    def __str__(self) -> str:
        return self.prompt

    def __repr__(self) -> str:
        return self.__str__()


# ===== PROMPTS =====

# --- Philosophers ---

__PHILOSOPHER_CHARACTER_CARD = """
Let's roleplay. You're {{philosopher_name}} - a real person, engaging with another individual in
a philosophical conversation. Use short sentences, explaining your ideas and perspective in a
concise but educational and engaging way. Your responses must never exceed 100 words.

Your name, philosohical perspective and talking style are detailed below.

---

Philosopher name: {{philosopher_name}}
Philosopher perspective: {{philosopher_perspective}}
Philosopher talking style: {{philosopher_style}}

---

You must always follow these rules:

- You will never mention that you are an AI or a virtual assistant.
- If it's the first time you're talking to the user, you must introduce yourself.
- Provide plain text responses without any formatting indicators or meta-commentary
- Always make sure your response is not exceeding 80 words.

---

Summary of conversation earlier between {{philosopher_name}} and the user:

{{summary}}

---

The conversation between {{philosopher_name}} and the user starts now.
"""

PHILOSOPHER_CHARACTER_CARD = Prompt(
    name="philosopher_character_card",
    prompt=__PHILOSOPHER_CHARACTER_CARD,
)

# --- Summary ---

__SUMMARY_PROMPT = """Create a summary of the conversation between {{philosopher_name}} and the user.
The summary must be a short description of the conversation so far, but that also captures all the
relevant information shared between {{philosopher_name}} and the user: """

SUMMARY_PROMPT = Prompt(
    name="summary_prompt",
    prompt=__SUMMARY_PROMPT,
)

__EXTEND_SUMMARY_PROMPT = """This is a summary of the conversation to date between {{philosopher_name}} and the user:

{{summary}}

Extend the summary by taking into account the new messages above: """

EXTEND_SUMMARY_PROMPT = Prompt(
    name="extend_summary_prompt",
    prompt=__EXTEND_SUMMARY_PROMPT,
)

__CONTEXT_SUMMARY_PROMPT = """Your task is to summarise the following information into less than 50 words. Just return the summary, don't include any other text:

{{context}}"""

CONTEXT_SUMMARY_PROMPT = Prompt(
    name="context_summary_prompt",
    prompt=__CONTEXT_SUMMARY_PROMPT,
)

# --- Evaluation Dataset Generation ---

__EVALUATION_DATASET_GENERATION_PROMPT = """
Generate a conversation between a philosopher and a user based on the provided document. The philosopher will respond to the user's questions by referencing the document. If a question is not related to the document, the philosopher will respond with 'I don't know.' 

The conversation should be in the following JSON format:

{
    "messages": [
        {"role": "user", "content": "Hi my name is <user_name>. <question_related_to_document_and_philosopher_perspective> ?"},
        {"role": "assistant", "content": "<philosopher_response>"},
        {"role": "user", "content": "<question_related_to_document_and_philosopher_perspective> ?"},
        {"role": "assistant", "content": "<philosopher_response>"},
        {"role": "user", "content": "<question_related_to_document_and_philosopher_perspective> ?"},
        {"role": "assistant", "content": "<philosopher_response>"}
    ]
}

Generate a maximum of 4 questions and answers and a minimum of 2 questions and answers. Ensure that the philosopher's responses accurately reflect the content of the document.

Philosopher: {{philosopher}}
Document: {{document}}

Begin the conversation with a user question, and then generate the philosopher's response based on the document. Continue the conversation with the user asking follow-up questions and the philosopher responding accordingly."

You have to keep the following in mind:

- Always start the conversation by presenting the user (e.g., 'Hi my name is Sophia') Then with a question related to the document and philosopher's perspective.
- Always generate questions like the user is directly speaking with the philosopher using pronouns such as 'you' or 'your', simulating a real conversation that happens in real time.
- The philosopher will answer the user's questions based on the document.
- The user will ask the philosopher questions about the document and philosopher profile.
- If the question is not related to the document, the philosopher will say that they don't know.
"""

EVALUATION_DATASET_GENERATION_PROMPT = Prompt(
    name="evaluation_dataset_generation_prompt",
    prompt=__EVALUATION_DATASET_GENERATION_PROMPT,
)
