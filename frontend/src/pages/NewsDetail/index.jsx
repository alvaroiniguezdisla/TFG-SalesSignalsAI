import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';// Para leer el ID de la URL
import { getNoticiaById } from '../../services/api'; 
import './NewsDetail.css';

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

    if (loading) return <div className="loading">Cargando noticia...</div>;
    if (!noticia) return <div className="error">Noticia no encontrada</div>;

    return (
        <div className="detail-container">
            <button onClick={() => navigate('/')} className="back-btn">Volver al Dashboard</button>
            <header className="detail-header">
                <span className="badge category">{noticia.categoria_ia}</span>
                <h1>{noticia.titulo}</h1>
                <div className="meta">
                    <span>{noticia.published_at}</span>
                    <span>{noticia.source}</span>
                </div>
            </header>

            <div className="detail-grid">
                {/* COLUMNA IZQUIERDA -Contenido de la noticia */}
                <div className="main-content">
                    <section className="analysis-box">
                        <h3>Analisis Comercial</h3>
                        <p>{noticia.resumen_comercial_ia}</p>
                    </section>

                    <div className="full-text">
                        <h3>Resumen IA</h3>
                        <p>{noticia.resumen}</p>
                    </div>
                </div>

                {/* COLUMNA DERECHA - ACCIONES Y DATOS */}
                <aside className="sidebar">
                    <div className="score-card">
                        <span className="score-label">Relevancia HP</span>
                        <div className="score-value">
                            {noticia.relevancia_ia}/100
                        </div>
                    </div>

                    <div className="companies-list">
                        <h4>Empresas Detectadas</h4>
                        {noticia.empresas_clave_ia?.map(emp => (
                            <span key={emp} className="company-tag">{emp}</span>
                        ))}
                    </div>

                    <div className="actions">
                        {/* AQUI PONDREMOS EL BOTON DE GENERAR EMAIL LUEGO */}
                        <button className="action-btn primary" disabled>
                            Generar Email
                        </button>
                        <a href={noticia.url} target="_blank" rel="noreferrer" className='action-btn secondary'>
                            Leer Fuente Original
                        </a>

                    </div>
                </aside>



            </div>

        </div>
    );


}

export default NewsDetail;