import React from 'react';
import { useNavigate } from 'react-router-dom';
import './NewsCard.css';

/**
 * Componente Tarjeta Inteligente (Smart Card) 
 * Aprovecha todas las columnas disponibles y mejora la legibilidad.
 */
function NewsCard({ noticia, userCompanies =[] }) {
    const navigate = useNavigate();
    const getPriorityLevel =(relevancia)=>{
        if (relevancia >= 70) return {label: 'Alta',class: 'priority-high' };
        if (relevancia >= 40) return {label: 'Media', class: 'priority-medium' };
        return {label: 'Baja', class: 'priority-low' };
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

            {/* 1.5 RELEVANCIA */}
            <div className="card-relevance-bar">
                <span className="relevance-label">Relevancia: </span>
                {getRelevanceBadge(noticia.relevancia_ia)}
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

                {/* 0. Fuentes (Solicitud Usuario) */}
                <div className="context-row">
                    <span className="context-label">Fuente Principal:</span>
                    <span className="source-tag">{noticia.fuente || 'Desconocida'}</span>
                </div>

                {noticia.urls_extra && noticia.urls_extra.length > 0 && (
                    <div className="context-row">
                        <span className="context-label">Otras Fuentes:</span>
                        <div className="tags-list">
                            {noticia.urls_extra.map((url, idx) => (
                                <a key={idx} href={url} target="_blank" rel="noopener noreferrer" className="extra-source-link">Source {idx + 1}</a>
                            ))}
                        </div>
                    </div>
                )}

                {/* 1. Categoria  */}
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

                {/* 3. Empresas Clave */}
                <div className="context-row">
                    <span className="context-label">Empresas:</span>
                    <div className="tags-list">
                        {noticia.empresas_clave_ia && noticia.empresas_clave_ia.length > 0 ? (
                            noticia.empresas_clave_ia.map((empresa, idx) => (
                                <span key={idx} className="company-tag">#{empresa}</span>
                            ))
                        ) : (
                            <span className="company-tag">Desconocidas</span>
                        )}
                    </div>
                </div>
            </div>

            {/* 4. ACCIÓN */}
            <div className="card-footer">
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
