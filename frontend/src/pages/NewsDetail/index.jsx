import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';// Para leer el ID de la URL
import { getNoticiaById } from '../../services/api';
import useFeedback from '../../hooks/useFeedback';
import './NewsDetail.css';
import Spinner from '../../components/Spinner';
import BackToDashboardButton from '../../components/BackToDashboardButton';

function NewsDetail() {
    const { id } = useParams(); //sacamos el id de la URL
    const { feedbacks, toggleFeedback } = useFeedback();

    const [noticia, setNoticia] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            setLoading(true);
            const data = await getNoticiaById(id);
            setNoticia(data);
            setLoading(false);
        }
        loadData();
    }, [id]);

    if (loading) return <Spinner message="Cargando noticia..." />;
    if (!noticia) return <div className="error">Noticia no encontrada</div>;

    return (
        <div className="detail-container">
            <BackToDashboardButton />

            {/* CABECERA: Título y Categorías */}
            <header className="detail-header">
                <h1>{noticia.titulo}</h1>

                <div className="meta-row">
                    <div className="source-column">
                        {/* Fuente de origen principal */}
                        <span className="meta-item source">
                            Fuente: <strong>{noticia.fuente}</strong>
                        </span>
                        {/* Fuentes secundarias estructuradas desde JSON */}
                        {noticia.urls_extra && Array.isArray(noticia.urls_extra) && noticia.urls_extra.length > 0 && (
                            <div className="extra-sources">
                                <span className="extra-label">También en:</span>
                                {noticia.urls_extra.map((fuente_secundaria, i) => (
                                    <a
                                        key={i}
                                        href={fuente_secundaria.url || fuente_secundaria} // Soporte de retrocompatibilidad para registros anteriores
                                        target="_blank"
                                        rel="noreferrer"
                                        className="extra-source-link"
                                    >
                                        {fuente_secundaria.fuente || `Fuente ${i + 1}`}
                                    </a>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="dates-row">
                        <span className="meta-item date">
                            Publicado: {noticia.published_at
                                ? new Date(noticia.published_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
                                : "Fecha desconocida"}
                        </span>
                        <span className="meta-item date-scraped">
                            Detectado: {noticia.scraped_at
                                ? new Date(noticia.scraped_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
                                : "-"}
                        </span>
                    </div>
                </div>
            </header>

            <div className="detail-grid">

                {/* COLUMNA PRINCIPAL */}
                <div className="main-content">

                    {/* Análisis IA */}
                    <section className="analysis-box">
                        <h3>Análisis de Oportunidad (IA)</h3>
                        <p>{noticia.resumen_comercial_ia || "No hay análisis disponible."}</p>
                    </section>

                    {/* Guía de Conversación */}
                    {noticia.talk_track_ia && (
                        <section className="analysis-box">
                            <h3>Guía de Conversación</h3>
                            <div className="talk-track-content">
                                {noticia.talk_track_ia.split('\n').filter(Boolean).map((punto, i) => (
                                    <p key={i}>{punto}</p>
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Borrador de Email */}
                    {noticia.email_draft_ia && (
                        <section className="analysis-box email-draft">
                            <h3>Borrador de correo</h3>
                            <pre className="email-content">{noticia.email_draft_ia}</pre>
                            <button
                                className="action-btn primary"
                                onClick={() => navigator.clipboard.writeText(noticia.email_draft_ia)}
                            >
                                Copiar Email
                            </button>
                        </section>
                    )}

                    {/* Resumen Original */}
                    <section className="full-text">
                        <h3>Resumen Original</h3>
                        <p>{noticia.resumen || "Sin resumen disponible."}</p>
                    </section>
                </div>

                {/* BARRA LATERAL */}
                <aside className="sidebar">

                    {/* 1. Relevancia (Barra) */}
                    <div className="score-card">
                        <span className="score-label">Relevancia</span>
                        <div className="score-value-container">
                            <span className="score-number">{noticia.relevancia_ia}</span>
                            <span className="score-max">/100</span>
                        </div>
                        <div className="score-bar-bg">
                            <div
                                className="score-bar-fill"
                                style={{ width: `${noticia.relevancia_ia}%` }}
                            ></div>
                        </div>
                    </div>

                    {/* 2. Empresas (con tamaño si disponible) */}
                    <div className="sidebar-section">
                        <h4>Empresas</h4>
                        <div className="tags-wrapper">
                            {noticia.empresas_detalle_ia && noticia.empresas_detalle_ia.length > 0 ? (
                                noticia.empresas_detalle_ia.map((emp, i) => {
                                    const sizeClass = emp.tamano === 'Gran Cuenta' ? 'tag-size-gran-cuenta'
                                        : emp.tamano === 'Mediana Empresa' ? 'tag-size-mediana'
                                            : emp.tamano === 'PYME' ? 'tag-size-pyme'
                                                : emp.tamano === 'Startup' ? 'tag-size-startup'
                                                    : '';
                                    return (
                                        <span key={i} className="tag-pill">
                                            {emp.nombre}
                                            {emp.tamano && (
                                                <span className={`tag-size ${sizeClass}`}>{emp.tamano}</span>
                                            )}
                                        </span>
                                    );
                                })
                            ) : noticia.empresas_clave_ia && noticia.empresas_clave_ia.length > 0 ? (
                                noticia.empresas_clave_ia.map((emp, i) => (
                                    <span key={i} className="tag-pill">{emp}</span>
                                ))
                            ) : (
                                <span className="no-data">No se detectaron empresas</span>
                            )}
                        </div>
                    </div>

                    {/* 3. Categorías (Movido aquí) */}
                    <div className="sidebar-section">
                        <h4>Categorías</h4>
                        <div className="categories-list">
                            {/* Señal */}
                            <div className="category-item signal">
                                <span className="label">Categoría:</span>
                                <span className="value">{noticia.categoria_ia || "-"}</span>
                            </div>

                            {/* Producto */}
                            {noticia.categoria_producto_ia && (
                                <div className="category-item product">
                                    <span className="label">Categoría Producto:</span>
                                    <span className="value">{noticia.categoria_producto_ia}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Botones Feedback */}
                    <div className="sidebar-section feedback-section">
                        <h4>¿Te ha resultado útil?</h4>
                        <div className="feedback-controls large">
                            <button
                                className={`feedback-btn like-btn ${feedbacks?.[noticia.url_hash] === 'like' ? 'active' : ''}`}
                                onClick={() => toggleFeedback(noticia.url_hash, 'like')}
                            >
                                👍 Me gusta
                            </button>
                            <button
                                className={`feedback-btn dislike-btn ${feedbacks?.[noticia.url_hash] === 'dislike' ? 'active' : ''}`}
                                onClick={() => toggleFeedback(noticia.url_hash, 'dislike')}
                            >
                                👎 No me gusta
                            </button>
                        </div>
                    </div>

                    {/* Botones */}
                    <div className="actions">
                        <a
                            href={noticia.url}
                            target="_blank"
                            rel="noreferrer"
                            className="action-btn secondary"
                        >
                            Leer Noticia Original
                        </a>
                    </div>
                </aside>
            </div>
        </div>
    );
}

export default NewsDetail;
