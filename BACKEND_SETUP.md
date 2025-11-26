
Backend Server Installation and Startup Instructions

1. First setup your python environment. Conda is the reccomended tool for creating the python environments.
  - The command to setup your environment is: `conda create --name <env_name> --file backend_requirements.txt`

2. Once that has successfully installed activate the environment with: conda activate <env_name>

3. Install the required spaCy language models for semantic comparison:
```bash
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
python -m spacy download de_core_news_sm
python -m spacy download es_core_news_sm
python -m spacy download it_core_news_sm
python -m spacy download pt_core_news_sm
python -m spacy download nl_core_news_sm
```

4. Now navigate to the fastapi/app/ directory

5. To start the server run: `fastapi dev main.py` 


