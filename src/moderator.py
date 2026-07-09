import json
import os

from dotenv import load_dotenv
from groq import Groq

from config import GROQ_MODEL_NAME

load_dotenv()

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def _load_prompts():
    path = os.path.join(PROMPTS_DIR, "moderator_system_prompt.txt")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    question_prompt, answer_prompt = content.split("---SEPARATOR---")
    return question_prompt.strip(), answer_prompt.strip()


QUESTION_CHECK_PROMPT, ANSWER_CHECK_PROMPT = _load_prompts()

class Moderator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def _call_json(self, prompt):
        response = self.client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message.content.strip()
        content = content.strip("`").removeprefix("json").strip()
        return json.loads(content)

    def check_question(self, question):
        """Renvoie (autorisee: bool, raison: str)."""
        try:
            result = self._call_json(QUESTION_CHECK_PROMPT.format(question=question))
            return result.get("autorisee", False), result.get("raison", "")
        except (json.JSONDecodeError, KeyError):
            return False, "Erreur de modération, question bloquée par précaution."
        except Exception:
            return False, "Service de modération indisponible, question bloquée par précaution."

    def check_answer(self, question, contexte, reponse):
        """Renvoie (valide: bool, raison: str)."""
        try:
            prompt = ANSWER_CHECK_PROMPT.format(
                question=question, contexte=contexte, reponse=reponse
            )
            result = self._call_json(prompt)
            return result.get("valide", False), result.get("raison", "")
        except (json.JSONDecodeError, KeyError):
            return False, "Erreur de validation, réponse bloquée par précaution."
        except Exception:
            return False, "Service de validation indisponible, réponse bloquée par précaution."


if __name__ == "__main__":
    moderator = Moderator()