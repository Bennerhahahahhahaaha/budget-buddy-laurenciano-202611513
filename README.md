### Budget Buddy!

Its a personal finance dashboard built with Python, Streamlit, and Matplotlib. You set up a budget for a month and then you log your expenses throughout the month. You will then be able to see how you fare up against your made budget and see if you can make any changes. 

How to set it up: 

1. Clone the repository
2. Create a virtual environment using the command:

python3 -m venv SP1

3. Activate the virtual environment 

macOS / Linux:

   source SP1/bin/activate

Windows (PowerShell): 

   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   SP1\Scripts\activate

4. Install the following libraries:

   pip install matplotlib streamlit

5. Try it now!

   streamlit run main.py

#HOW TO USE IT: 

1. **Budget Tab**, you make a budget first, choose the month and year(default is the current month for easy setup), enter an income source and allocate it on the categories
2. **Expenses Tab** log your expenses per day, if you make a mistake just edit it on the table below
3. **Home** You can check your progress and your financial state through the graphs!

### Known Limitations

1. Without clicking Save Budget, the changes you're working on aren't saved so be sure to save them!
2. Only 1 income source is allowed, so multiple income sources is unsupported.
3. The font is loaded from google fonts so the website doesn't load the font.
4. No Dark Mode