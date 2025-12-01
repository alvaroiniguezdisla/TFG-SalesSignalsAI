import React from 'react';

/**
 * Componente que muestra una noticia individual.
 * Recibe la noticia como 'prop'.
 */
function NewsCard({ noticia }) {
    return (
        <div className="news-card">
            <h2>{noticia.titulo}</h2>
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
