import json
import time
from typing import Any
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

# --- CONFIGURATION ---
INPUT_FILE = "questions.json"
OUTPUT_FILE = "improved_questions.json"

# 1. CHANGE HERE: Point the OpenAI client to your local Ollama server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" # The library requires an API key, but Ollama ignores it
)

# You can change this to whichever model you downloaded via Ollama (e.g., "mistral", "llama3")
LOCAL_MODEL = "llama3.2"

# Only questions longer than this or flagged by AI will be changed
CHAR_THRESHOLD = 80

def should_improve(question_text: str) -> bool:
    """
    Initial filter: Flag questions that are long or use complex phrasing.
    You can add custom logic here.
    """
    if len(question_text) > CHAR_THRESHOLD:
        return True

    # Add specific jargon you want to target
    jargon = ["utilize", "pertaining", "subsequent"]
    return any(word in question_text.lower() for word in jargon)


def improve_question(question_obj: dict[str, Any]) -> str:
    """
    Sends the question to the AI to be simplified while preserving meaning.
    """
    prompt = f"""
Rewrite the following quiz question to be clearer and easier to understand.
- Keep the meaning identical.
- Keep it professional but accessible.
- Ensure the 'correctAnswer' still makes sense with the new text.
- Return ONLY the rewritten text.

Original: {question_obj["text"]}
"""

    messages: list[ChatCompletionMessageParam] = [
        ChatCompletionUserMessageParam(
            role="user",
            content=prompt,
        )
    ]

    try:
        # 2. CHANGE HERE: Use your local model instead of gpt-4o-mini
        response = client.chat.completions.create(
            model=LOCAL_MODEL,
            messages=messages,
            temperature=0.3,
        )

        rewritten_text = response.choices[0].message.content

        if rewritten_text is None:
            return question_obj["text"]

        return rewritten_text.strip()

    except Exception as e:
        print(f"Error processing ID {question_obj.get('id')}: {e}")
        return question_obj["text"]


def main() -> None:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        questions: list[dict[str, Any]] = json.load(f)

    improved_data: list[dict[str, Any]] = []
    total = len(questions)

    print(f"Starting process for {total} questions using local model: {LOCAL_MODEL}...")

    for index, q in enumerate(questions):
        # 1. Selection Check
        if should_improve(q["text"]):
            print(f"[{index + 1}/{total}] Improving: {q['id']}")
            original_text = q["text"]

            q["text"] = improve_question(q)

            # Log the change
            if original_text != q["text"]:
                print(f"   Done: {q['text']}")

            # I removed the time.sleep(0.1) because you don't have rate limits on your own machine!

        else:
            print(f"[{index + 1}/{total}] Skipping: {q['id']} (Already clear)")

        improved_data.append(q)

    # 3. Save the results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(improved_data, f, indent=2, ensure_ascii=False)

    print(f"\nSuccess! Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()