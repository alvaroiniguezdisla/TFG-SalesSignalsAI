import React from 'react';
import { useNavigate } from 'react-router-dom';
import useFeedback from '../../hooks/useFeedback';
import './NewsCard.css';

/**
 * Componente Tarjeta Inteligente (Smart Card) 
 * Aprovecha todas las columnas disponibles y mejora la legibilidad.
 */
function NewsCard({ noticia, userCompanies = [] }) {
    const navigate = useNavigate();
    const { feedbacks, toggleFeedback } = useFeedback();
    const currentFeedback = feedbacks ? feedbacks[noticia.url_hash] : undefined;

    const getPriorityLevel = (relevancia) => {
        if (relevancia >= 70) return { label: 'Alta', class: 'priority-high' };
        if (relevancia >= 40) return { label: 'Media', class: 'priority-medium' };
        return { label: 'Baja', class: 'priority-low' };
    };

    const priority = getPriorityLevel(noticia.relevancia_ia);

    // Detectar si es noticia nueva (< 24h)
    const isNew = () => {
        if (!noticia.scraped_at) return false;
        const diffHours = (new Date() - new Date(noticia.scraped_at)) / (1000 * 60 * 60);
        return diffHours < 24;
    };

    // Detectar si menciona un cliente seguido 
    const isMyClient = (noticia.empresas_clave_ia || []).some(empresa =>
        userCompanies.some(myCompany =>
            empresa.toLowerCase().includes(myCompany.toLowerCase())
        )
    );

    // 1. HELPERS para formato
    const formatDate = (dateString) => {
        if (!dateString) return 'Fecha desc.';
        return new Date(dateString).toLocaleDateString('es-ES', {
            day: 'numeric', month: 'short', year: 'numeric'
        });
    };

    // Color del semáforo (Relevancia) - VERSIÓN LIMPIA
    const getRelevanceBadge = (score) => {
        let colorClass = 'badge-low';

        if (score >= 70) { colorClass = 'badge-high'; }
        else if (score >= 40) { colorClass = 'badge-medium'; }

        return (
            <div className="relevance-indicator" title={`Relevancia IA: ${score}%`}>
                <span className={`relevance-dot ${colorClass}`}></span>
                <span className="relevance-score">{score || 0}%</span>
            </div>
        );
    };

    // 2. DECISIÓN DE CONTENIDO
    // Si tenemos resumen comercial (IA), lo priorizamos. Si no, usamos el resumen normal.
    const summaryText = noticia.resumen_comercial_ia || noticia.resumen || "Sin resumen disponible.";
    const isAiSummary = !!noticia.resumen_comercial_ia;

    // Categoría: Priorizamos IA, fallback a scraping
    const category = noticia.categoria_ia || noticia.categoria || "General";

    return (
        <div className="news-card" onClick={() => navigate(`/noticia/${noticia.url_hash}`)}>

            {/* 1. CABECERA: Badges */}
            <div className="card-header">
                <span className="date-text">{formatDate(noticia.published_at)}</span>
                <div className="badges-container">
                    {isNew() && <span className="new-badge">NUEVO</span>}
                    {isMyClient && <span className="client-badge">TU CLIENTE</span>}
                    <span className={`priority-badge ${priority.class}`}>{priority.label}</span>
                </div>
            </div>


            {/* 2. CONTENIDO PRINCIPAL */}
            <div className="card-body">
                <h3 className="card-title">{noticia.titulo}</h3>

                {/* Resumen: Solo si existe. Si es IA, estilo destacado. Si es raw, texto simple. */}
                {summaryText && summaryText !== "Sin resumen disponible." && (
                    <div className={`analysis-box ${isAiSummary ? 'ai-style' : 'raw-style'}`}>
                        {isAiSummary && <span className="analysis-label">Análisis IA</span>}
                        <p className="analysis-text">{summaryText}</p>
                    </div>
                )}

                {(!summaryText || summaryText === "Sin resumen disponible.") && (
                    <p className="no-summary-text">Sin resumen disponible</p>
                )}


            </div>

            {/* 3. CONTEXTO DE VENTA */}
            <div className="card-context">

                {/* Indicador de Relevancia del contenido */}
                <div className="context-row">
                    <span className="context-label">Relevancia:</span>
                    {getRelevanceBadge(noticia.relevancia_ia)}
                </div>

                {/* Origen principal de la noticia */}
                <div className="context-row">
                    <span className="context-label">Fuente Principal:</span>
                    <span className="source-tag">{noticia.fuente || 'Desconocida'}</span>
                </div>

                {/* Fuentes adicionales detectadas (Deduplicación estructurada) */}
                {noticia.urls_extra && Array.isArray(noticia.urls_extra) && noticia.urls_extra.length > 0 && (
                    <div className="context-row">
                        <span className="context-label">Otras Fuentes:</span>
                        <div className="tags-list">
                            {noticia.urls_extra.map((fuente_secundaria, idx) => (
                                <a
                                    key={idx}
                                    href={fuente_secundaria.url || fuente_secundaria}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="extra-source-link"
                                >
                                    {fuente_secundaria.fuente || `Fuente ${idx + 1}`}
                                </a>
                            ))}
                        </div>
                    </div>
                )}

                {/* Categoría de negocio asignada */}
                <div className="context-row">
                    <span className="context-label">Categoría:</span>
                    <span className="badge-category">
                        {category === "General" ? "Desconocida" : category}
                    </span>
                </div>

                {/* 2. Categoria de Producto */}
                <div className="context-row">
                    <span className="context-label">Categoría de Producto:</span>
                    <span className="product-pill">
                        {noticia.categoria_producto_ia && noticia.categoria_producto_ia !== 'Otros / No Aplica'
                            ? noticia.categoria_producto_ia
                            : 'Desconocida'}
                    </span>
                </div>

                {/* 3. Empresas Clave (con tamaño si disponible) */}
                <div className="context-row">
                    <span className="context-label">Empresas:</span>
                    <div className="tags-list">
                        {noticia.empresas_detalle_ia && noticia.empresas_detalle_ia.length > 0 ? (
                            noticia.empresas_detalle_ia.map((emp, idx) => (
                                <span key={idx} className="company-tag">
                                    #{emp.nombre}
                                    {emp.tamano && (
                                        <span className="company-size"> · {emp.tamano}</span>
                                    )}
                                </span>
                            ))
                        ) : noticia.empresas_clave_ia && noticia.empresas_clave_ia.length > 0 ? (
                            noticia.empresas_clave_ia.map((empresa, idx) => (
                                <span key={idx} className="company-tag">#{empresa}</span>
                            ))
                        ) : (
                            <span className="company-tag">Desconocidas</span>
                        )}
                    </div>
                </div>
            </div>

            {/* 4. ACCIÓN y FEEDBACK */}
            <div className="card-footer">
                <div className="feedback-controls" onClick={(e) => e.stopPropagation()}>
                    <button
                        className={`feedback-btn like-btn ${currentFeedback === 'like' ? 'active' : ''}`}
                        onClick={(e) => { e.stopPropagation(); toggleFeedback(noticia.url_hash, 'like'); }}
                        title="Me parece útil"
                    >
                        👍
                    </button>
                    <button
                        className={`feedback-btn dislike-btn ${currentFeedback === 'dislike' ? 'active' : ''}`}
                        onClick={(e) => { e.stopPropagation(); toggleFeedback(noticia.url_hash, 'dislike'); }}
                        title="No me parece útil"
                    >
                        👎
                    </button>
                </div>

                <a
                    href={noticia.url || noticia.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="read-more-link"
                    onClick={(e) => e.stopPropagation()}
                >
                    Leer noticia original →
                </a>
            </div>
        </div>
    );
}

export default NewsCard;
