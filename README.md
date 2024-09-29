# PRQA
This repository is the implementation and test results of PRQA(Pruning and Rewriting Question Answering to test Question Answering software).
This artifact contains:
1. implementation of PRQA
2. test results

## Instructions for using PRQA:
1. step 1: fill in the configuration needed in the file config.ini
2. step 2: run ```python run.py config.ini``` to get the test results of all new generated test cases
3. step 3: run ```python answerAnalysis.py config.ini``` to get the analysis of results, including the number of proportion of MR violations and the MR violation test datasets

## Test results:
Test results for pre-trained QA model and LLMs are stored in two directory: ```results/pre-train``` and ```results/gpt```, respectively.
