from bs4 import BeautifulSoup
from unicodedata import normalize as normalize_unicode
from typing import Optional



def _normalize_text(raw_text: str) -> str:
    cleaned_txt =  " ".join(raw_text.split())
    return normalize_unicode('NFKC', cleaned_txt)


def get_text_by_id(html: str, element_id: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find(id=element_id)
    if element:
        return _normalize_text(element.text.strip())
    return None




    


