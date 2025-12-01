import requests
from bs4 import BeautifulSoup


def obtener_noticias():
    url= "https://elpais.com/"
    response= requests.get(url)

    if response.status_code==200:
        soup= BeautifulSoup(response.text,'html.parser')
        noticias =[]

        # En El País, las noticias suelen estar en etiquetas <article>
        articulos = soup.find_all('article')

        for articulo in articulos[:10]:
            #Buscamos el titular, que suele ser un h2
            titulo_tag= articulo.find('h2')
            if titulo_tag:
                link_tag = titulo_tag.find('a')
                if link_tag:
                    titulo = link_tag.text.strip()
                    link =link_tag['href']

                    #A veces los enlaces son relativos (empiezan por  /), hay que ponerles el https://elpais.com/ delante
                    if link.startswith('/'):
                        link = f'https://elpais.com{link}'

                    noticias.append({
                        'titulo': titulo,
                        'link': link
                    })


        return noticias
    else:

        return []

            
