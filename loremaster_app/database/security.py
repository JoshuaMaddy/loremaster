from bs4 import BeautifulSoup as bs

def clean_html(html:str) -> str:
    soup = bs(html, features='lxml')

    for script in soup("script"):
        script.extract()
    
    for link in soup("link"):
        link.extract()

    return(soup.prettify()[15:-17])