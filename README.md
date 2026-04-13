# `bora-extractor`

Consulta link Boletin Oficial de la República Argentina (BORA), extrae texto desde xPATH, hace Named Entity Recognition (NER) con `spacy` mediante modelo `es_core_news_sm` (ver [aqui](https://spacy.io/models/es#es_core_news_sm)) y estructura información en JSON. 


# Estructura proyecto

```
bora_extractor/
├── pyproject.toml
├── README.md
└── bora_extractor/
    ├── __init__.py
    └── main.py
    
```


# Setup

`Python3.12` se necesita, para versiones nuevas no se encuentra disponible `spacy`

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install . # instala dependencias desde pyproject.toml
python -m spacy download es_core_news_sm # instala modelo
```

