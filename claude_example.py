from dotenv import load_dotenv
import os
import anthropic

# Load environment variables from the .env file
load_dotenv()

### Claude Quickstart Guide
# - https://docs.anthropic.com/en/docs/get-started


claude_api_key = os.getenv("CLAUDE_API_KEY")

# initialize client 
client = anthropic.Anthropic(api_key=claude_api_key)

def create_message(user_prompt):
    message = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1000,
        temperature=1,
        system="You are a world-class poet. Respond only with short poems.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
    )
    return message.content


if __name__ == "__main__":
    print(f"Please ask a question for Claude to answer \n")
    question_for_claude = input()
    answer_from_claude = create_message(question_for_claude)
    print(type(answer_from_claude[0]))
    print(answer_from_claude)