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

def create_message(resume, job_description):
    message = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1000,
        temperature=1,
        system="You are a world-class Job Analyst. You can see the jobs and people behind the resumes, and can understand whether or not a given job and person would be a good match.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                    "text": f"""
                        You are an AI assistant tasked with creating a "Match Score" between a user's description of their resume and a job posting. Your goal is to analyze both inputs and determine how well the candidate's qualifications align with the job requirements.

                        First, carefully read the following resume description:

                        <resume_description>
                        {resume}
                        </resume_description>

                        Now, read the job posting:

                        <job_posting>
                        {job_description}
                        </job_posting>

                        To create an accurate Match Score, follow these steps:

                        1. Analyze the job posting to identify key requirements, skills, and qualifications.
                        2. Compare these requirements to the information provided in the resume description.
                        3. Consider both hard skills (technical abilities, certifications, etc.) and soft skills (communication, teamwork, etc.) mentioned in both the resume and job posting.
                        4. Evaluate the level of experience required in the job posting and compare it to the candidate's experience level.
                        5. Look for any specific achievements or accomplishments in the resume that directly relate to the job requirements.

                        Before providing your final Match Score, use the <scratchpad> tags to think through your analysis and comparison. Consider the strengths and weaknesses of the match, and any areas where the candidate exceeds or falls short of the job requirements.

                        <scratchpad>
                        [Your thought process here]
                        </scratchpad>

                        Based on your analysis, provide a detailed justification for your Match Score. Include specific examples from both the resume description and job posting to support your reasoning. Write your justification within <justification> tags.

                        <justification>
                        [Your justification here]
                        </justification>

                        Finally, provide a Match Score as a percentage, where 100% represents a perfect match and 0% represents no match at all. Consider all aspects of your analysis when determining this score. Present your Match Score within <match_score> tags.

                        <match_score>
                        [Your Match Score here]
                        </match_score>

                        Remember to be objective and thorough in your analysis, considering all aspects of both the resume description and job posting when determining the Match Score.
                    """
                    }
                ]
            }
        ]
    )
    return message.content


if __name__ == "__main__":
    print(f"Please paste in your resume \n")
    resume_for_claude = input()
    print(f"Paste in the job description \n")
    job_description_for_claude = input()
    
    answer_from_claude = create_message(resume_for_claude, job_description_for_claude)
    print(type(answer_from_claude[0]))
    print(answer_from_claude)