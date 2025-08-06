# Crossword-AI

# ✏️ Crossword Puzzle Generator using CSP & Backtracking

This project implements an AI that generates complete crossword puzzles using constraint satisfaction techniques. Given a grid structure and a list of words, it assigns each variable (a sequence of squares) a word that satisfies unary constraints (length) and binary constraints (character overlaps). Built with Python 3.12 as part of CS50’s AI course.

## 🧩 Overview

The goal is to solve crossword puzzles by modeling them as **Constraint Satisfaction Problems (CSP)**. The crossword consists of variables representing horizontal/vertical word slots. Each variable must be assigned a word:
- That matches its length (unary constraint)
- Whose overlapping letters match with neighboring variables (binary constraint)
- That hasn't already been used elsewhere

## 🚀 Getting Started

### Requirements

- Python 3.12
- Pillow (for rendering crossword images)

### Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/crossword-ai.git
   cd crossword-ai
   pip3 install Pillow

   python generate.py data/structure1.txt data/words1.txt output.png


   crossword/
│
├── data/                  # Grid structure and word list files
│   ├── structure1.txt     # Grid layout using _ for blank cells
│   └── words1.txt         # Word list for puzzle generation
│
├── crossword.py           # Defines Variable and Crossword classes
├── generate.py            # Main AI logic for generating crossword
└── README.md              # You're reading it!


$ python generate.py data/structure1.txt data/words1.txt output.png

██████████████
███████M████R█
█INTELLIGENCE█
█N█████N████S█
█F██LOGIC███O█
█E█████M████L█
█R███SEARCH█V█
███████X████E█
██████████████



