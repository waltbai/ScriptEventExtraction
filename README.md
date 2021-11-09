# ScriptEventExtraction
Script event extraction via AMR parser.

This is code for script extraction from narrative texts.
Specifically, it applies an AMR parser to extract event frames from texts.
Then, it utilizes a coreference resolution tool to find coreferred entities.
Finally, events are structured into graph/sequences via the coreference information.

## Corpus
This code use NYT portion of Gigaword Corpus as input.
The corpus can be found in [LDC](https://catalog.ldc.upenn.edu/LDC2011T07).

## Installation
### Dependencies
Use
```pip install -r requirements.txt```
to install dependencies.

### Models
Download english model for spacy:

```python -m spacy download en_core_web_sm```

Download wordnet and wordnet_ic for nltk:

```
>>> import nltk
>>> nltk.download("wordnet")
>>> nltk.download("wordnet_ic")
```

Download gsii parser model for amrlib following 
[official instructions](https://amrlib.readthedocs.io/en/latest/install/).

## Dataset construct instructions
### Arguments
The main arguments for each step are:
```
--corp_dir: the decompressed directory of gigaword corpus
--work_dir: the directory to store dataset
```

### Instructions
Step 1: extract documents

```python step_1.py --corp_dir <corp_dir> --work_dir <work_dir>```

Step 2: tokenize documents

```python step_2.py --work_dir <work_dir>```

Step 3: parse documents with amr parser

```python step_3.py --work_dir <work_dir>```

Step 4: coreference resolution

```python step_4.py --work_dir <work_dir>```

Step 5: extract events

```python step_5.py --work_dir <work_dir>```

Step 6: build script

```python step_6.py --work_dir <work_dir>```

