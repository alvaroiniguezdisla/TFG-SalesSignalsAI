import React from 'react';
import { useNavigate } from 'react-router-dom';
import './NewsCard.css';

/**
 * Componente Tarjeta Inteligente (Smart Card) 
 * Aprovecha todas las columnas disponibles y mejora la legibilidad.
 */
function NewsCard({ noticia }) {
    const navigate = useNavigate();

    // 1. HELPERS para formato
    const formatDate = (dateString) => {
        if (!dateString) return 'Fecha desc.';
        return new Date(dateString).toLocaleDateString('es-ES', {
            day: 'numeric', month: 'short', year: 'numeric'
        });
    };

    // Color del semáforo (Relevancia)
    const getRelevanceBadge = (score) => {
        let colorClass = 'badge-low';
        let label = 'BAJA';

        if (score >= 70) { colorClass = 'badge-high'; label = 'ALTA'; }
        else if (score >= 40) { colorClass = 'badge-medium'; label = 'MEDIA'; }

        return (
            <span className={`badge ${colorClass}`} title={`Relevancia IA: ${score}%`}>
                {label} ({score || 0}%)
            </span>
        );
    };

    // 2. DECISIÓN DE CONTENIDO
    // Si tenemos resumen comercial (IA), lo priorizamos. Si no, usamos el resumen normal.
    const summaryText = noticia.resumen_comercial_ia || noticia.resumen || "Sin resumen disponible.";
    const isAiSummary = !!noticia.resumen_comercial_ia;

    // Categoría: Priorizamos IA, fallback a scraping
    const category = noticia.categoria_ia || noticia.categoria || "General";

    return (
        <div className="news-card" onClick={() =>
            navigate(`/noticia/${noticia.url_hash}`)}
            style={{ cursor: 'pointer' }}>

            {/* --- CABECERA SUPERIOR: Categoría y Fecha --- */}
            <div className="card-top-meta">
                <span className="meta-category">{category}</span>
                <span className="meta-date">{formatDate(noticia.published_at)}</span>
            </div>

            {/* --- CUERPO PRINCIPAL --- */}
            <div className="card-body">
                <h2 className="card-title" title={noticia.titulo}>
                    {noticia.titulo}
                </h2>

                <div className="card-metrics">
                    {getRelevanceBadge(noticia.relevancia_ia)}
                    <span className="meta-source">Fuente: {noticia.fuente || 'El País'}</span>
                </div>

                {/* Resumen Diferenciado */}
                <div className={`card-summary ${isAiSummary ? 'summary-ai' : 'summary-raw'}`}>
                    {isAiSummary && <strong> Análisis Comercial: </strong>}
                    {summaryText}
                </div>
            </div>

            {/* --- PIE: Tags y CTA --- */}
            <div className="card-footer">
                {noticia.empresas_clave_ia && noticia.empresas_clave_ia.length > 0 ? (
                    <div className="tags-container">
                        {noticia.empresas_clave_ia.map((empresa, index) => (
                            <span key={index} className="tag">#{empresa}</span>
                        ))}
                    </div>
                ) : (
                    <div className="tags-placeholder"></div> /* Espacio vacío para alinear */
                )}

                <a
                    href={noticia.url || noticia.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-read-more"
                    onClick={(e) => e.stopPropagation()}
                >
                    Leer noticia→
                </a>
            </div>
        </div>
    );
}

export default NewsCard;
