


## Virtual Enviornment Set up
### Install VENV if not already installed
* 


### Create a Virtual Environment
* `python -m venv venv`

### Activate the Virtual Enviornment
* `source venv/bin/activate`

### Set your VS Code to use the VENV
* Note - You may need to close and re-open VS Code.
1. Press Ctrl+Shift+P (or Cmd+Shift+P on Mac) to open the Command Palette.
2. Type Python: Select Interpreter and hit Enter.
3. You should see a list that includes:
    1. ./.venv/bin/python (Linux/macOS)
    2. .venv\Scripts\python.exe (Windows) 
4. Select the one pointing to your .venv.
    1. If you don’t see it: Click "Enter interpreter path" → "Find..." → manually navigate to your .venv/bin/python or .venv/Scripts/python.exe.
5. Confirm it’s working
    1. Open a Python file
    2. Look in the bottom-left of VS Code — it should show your .venv as the active interpreter.
    3. You can also run: 
        `
        import sys
        print(sys.executable)
        ` in python


## Requirements
### Load requirements
* `pip install -r requirements.txt`

### How to create Base Requirements (when creating an environment)
#### Install all requirements needed
* `pip install requests beautifulsoup4`

#### Save requirements
* `pip freeze > requirements.txt`


### Playwright
* `pip install playwright`
* `playwright install`




pip install python-dotenv

### To update requirements.txt
pip freeze > requirements.txt

### Next time
Practice with sending a list of different jobs to the Job Match Rater, and store the output in a database.
* Match Score
* Job title
* Date of Job Posting
* 1 Sentence Description of Job

### Other Oportunities
* Look into Playwrite more to allow us to scrape more jobs
* Look into accepting PDF's and transforming them to a formate usable by claude.
* Generating a customized resume for job postings based on the users orriginal resume.
