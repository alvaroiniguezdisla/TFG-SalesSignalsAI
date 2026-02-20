import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';// Para leer el ID de la URL
import { getNoticiaById } from '../../services/api';
import './NewsDetail.css';
import Spinner from '../../components/Spinner';
function NewsDetail() {
    const { id } = useParams(); //sacamos el id de la URL
    const navigate = useNavigate(); //para el boton de volver
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
            <button onClick={() => navigate('/')} className="back-btn">
                &larr; Volver al Dashboard
            </button>

            {/* CABECERA: Título y Categorías */}
            <header className="detail-header">
                <h1>{noticia.titulo}</h1>

                <div className="meta-row">
                    <div className="source-column">
                        <span className="meta-item source">
                            Fuente: <strong>{noticia.fuente}</strong>
                        </span>
                        {noticia.urls_extra && noticia.urls_extra.length > 0 && (
                            <div className="extra-sources">
                                <span className="extra-label">También en:</span>
                                {noticia.urls_extra.map((url, i) => (
                                    <a key={i} href={url} target="_blank" rel="noreferrer" className="extra-source-link">
                                        Fuente {i + 1}
                                    </a>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="dates-row">
                        <span className="meta-item date">
                            Publicado: {noticia.published_at || "Fecha desconocida"}
                        </span>
                        <span className="meta-item date-scraped">
                            Detectado: {noticia.scraped_at ? new Date(noticia.scraped_at).toLocaleDateString() : "-"}
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

                    {/* 2. Empresas */}
                    <div className="sidebar-section">
                        <h4>Empresas</h4>
                        <div className="tags-wrapper">
                            {noticia.empresas_clave_ia && noticia.empresas_clave_ia.length > 0 ? (
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