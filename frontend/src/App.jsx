import { useEffect, useState } from 'react'
import './App.css'

function App() {
  //nos creamos una variable para guardar las noticias que nos traigamos 
  const [noticias, setNoticias] = useState([])

  useEffect(() => {
    //LLamamos a nuestro backend al puerto 8000
    fetch('http://localhost:8000/noticias')
      .then(response => response.json())
      .then(data => setNoticias(data))
      .catch(error => console.error("Error cargando noticias", error))
  }, [])

  //Aqui dibujamos lo que ve el usuario (el HTML)
  return (
    <div className="app-container">
      <h1> Observatorio de Señales</h1>

      {/* Creamos una rejilla para poner las noticias */}
      <div className="news-grid">
        {noticias.map((noticia, index) => (
          <div key={index} className="news-card">
            <h2>{noticia.titulo}</h2>
            <a href={noticia.link} target="_blank" rel="noopener noreferrer">
              Leer más en El País
            </a>

          </div>
        ))}
      </div>

    </div>
  )
}

export default App