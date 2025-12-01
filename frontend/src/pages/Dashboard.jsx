import { useEffect, useState } from 'react';
import { getNoticias } from '../services/api';
import NewsCard from '../components/NewsCard';

function Dashboard() {
    const [noticias, setNoticias] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadNews = async () => {
            try {
                setLoading(true);
                const data = await getNoticias();
                setNoticias(data);
            } catch (err) {
                setError("No se pudieron cargar las noticias. ¿Está el backend encendido?");
            } finally {
                setLoading(false);
            }
        };

        loadNews();
    }, []);

    if (loading) return <div className="loading">Cargando señales...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="dashboard">
            <header>
                <h1>📡 Observatorio de Señales</h1>
                <p>Monitorización en tiempo real de El País</p>
            </header>

            <div className="news-grid">
                {noticias.map((noticia, index) => (
                    <NewsCard key={index} noticia={noticia} />
                ))}
            </div>
        </div>
    );
}

export default Dashboard;
