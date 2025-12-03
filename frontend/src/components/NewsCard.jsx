import React from 'react';

/**
 * Componente que muestra una noticia individual.
 * Recibe la noticia como 'prop'.
 */
function NewsCard({ noticia }) {
    return (
        <div className="news-card">
            <h2>{noticia.titulo}</h2>
            
            {/* NUEVO: Si hay resumen, píntalo. Si no, no hagas nada. */}
            {noticia.resumen && <p className="news-summary">{noticia.resumen}</p>}

            <p className="news-source">Fuente: El País</p>
            <a
                href={noticia.link}
                target="_blank"
                rel="noopener noreferrer"
                className="read-more"
            >
                Leer noticia completa →
            </a>
        </div>
    );
}

export default NewsCard;
