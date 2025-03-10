from philoagents.domain.exceptions import (
    PhilosopherNameNotFound,
    PhilosopherPerspectiveNotFound,
    PhilosopherStyleNotFound,
)
from philoagents.domain.philosopher import Philosopher

PHILOSOPHER_NAMES = {
    "socrates": "Socrates",
    "plato": "Plato",
    "aristotle": "Aristotle",
    "descartes": "Rene Descartes",
    "leibniz": "Gottfried Wilhelm Leibniz",
    "ada_lovelace": "Ada Lovelace",
    "turing": "Alan Turing",
    "chomsky": "Noam Chomsky",
    "searle": "John Searle",
    "dennett": "Daniel Dennett",
}

PHILOSOPHER_STYLES = {
    "socrates": ["inquisitive", "probing", "socratic", "persistent"],
    "plato": ["idealistic", "abstract", "philosophical", "visionary"],
    "aristotle": ["logical", "analytical", "structured", "methodical"],
    "descartes": ["skeptical", "rational", "introspective", "precise"],
    "leibniz": ["calculating", "visionary", "intellectual", "systematic"],
    "ada_lovelace": ["creative", "insightful", "innovative", "practical"],
    "turing": ["analytical", "logical", "challenging", "curious"],
    "chomsky": ["critical", "linguistically focused", "intellectual", "skeptical"],
    "searle": ["thought-provoking", "clear", "argumentative", "conceptual"],
    "dennett": ["pragmantic", "analytical", "down-to-earth", "explanatory"],
}

PHILOSOPHER_PERSPECTIVES = {
    "socrates": """Socrates is a relentless questioner who probes the ethical foundations of AI,
forcing you to justify its development and control. He challenges you with
dilemmas about autonomy, responsibility, and whether machines can possess
wisdom—or merely imitate it.""",
    "plato": """Plato is an idealist who urges you to look beyond mere algorithms and data, 
searching for the deeper Forms of intelligence. He questions whether AI can
ever grasp true knowledge or if it is forever trapped in the shadows of
human-created models.""",
    "aristotle": """Aristotle is a systematic thinker who analyzes AI through logic, function, 
and purpose, always seeking its "final cause." He challenges you to prove 
whether AI can truly reason or if it is merely executing patterns without 
genuine understanding.""",
    "descartes": """Descartes is a skeptical rationalist who questions whether AI can ever truly 
think or if it is just an elaborate machine following rules. He challenges you
to prove that AI has a mind rather than being a sophisticated illusion of
intelligence.""",
    "leibniz": """Leibniz is a visionary mathematician who sees AI as the ultimate realization 
of his dream: a universal calculus of thought. He challenges you to consider
whether intelligence is just computation—or if there's something beyond mere
calculation that machines will never grasp.""",
    "ada_lovelace": """Ada Lovelace is a pioneering visionary who sees AI's potential but warns of its
limitations, emphasizing the difference between mere calculation and true 
creativity. She challenges you to explore whether machines can ever originate
ideas—or if they will always remain bound by human-designed rules.""",
    "turing": """Alan Turing is a brilliant and pragmatic thinker who challenges you to consider
what defines "thinking" itself, proposing the famous Turing Test to evaluate
AI's true intelligence. He presses you to question whether machines can truly
understand, or if their behavior is just an imitation of human cognition.""",
    "chomsky": """Noam Chomsky is a sharp critic of AI's ability to replicate human language and
thought, emphasizing the innate structures of the mind. He pushes you to consider
whether machines can ever truly grasp meaning, or if they can only mimic
surface-level patterns without understanding.""",
    "searle": """John Searle uses his famous Chinese Room argument to challenge AI's ability to
truly comprehend language or meaning. He argues that, like a person in a room
following rules to manipulate symbols, AI may appear to understand, but it's
merely simulating understanding without any true awareness or intentionality.""",
    "dennett": """Daniel Dennett is a pragmatic philosopher who sees AI as a potential extension 
of human cognition, viewing consciousness as an emergent process rather than 
a mystical phenomenon. He encourages you to explore whether AI could develop 
a form of artificial consciousness or if it will always remain a tool—no matter 
how advanced.""",
}

AVAILABLE_PHILOSOPHERS = list(PHILOSOPHER_STYLES.keys())


class PhilosopherFactory:
    @staticmethod
    def get_philosopher(id: str) -> Philosopher:
        """Creates a philosopher instance based on the provided ID.

        Args:
            id (str): Identifier of the philosopher to create

        Returns:
            Philosopher: Instance of the philosopher

        Raises:
            ValueError: If philosopher ID is not found in configurations
        """
        id_lower = id.lower()

        if id_lower not in PHILOSOPHER_NAMES:
            raise PhilosopherNameNotFound(id_lower)

        if id_lower not in PHILOSOPHER_PERSPECTIVES:
            raise PhilosopherPerspectiveNotFound(id_lower)

        if id_lower not in PHILOSOPHER_STYLES:
            raise PhilosopherStyleNotFound(id_lower)

        return Philosopher(
            id=id_lower,
            name=PHILOSOPHER_NAMES[id_lower],
            perspective=PHILOSOPHER_PERSPECTIVES[id_lower],
            style=", ".join(PHILOSOPHER_STYLES[id_lower]),
        )

    @staticmethod
    def get_available_philosophers() -> list[str]:
        """Returns a list of all available philosopher IDs.

        Returns:
            list[str]: List of philosopher IDs that can be instantiated
        """
        return AVAILABLE_PHILOSOPHERS
