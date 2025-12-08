import { useState } from 'react';
import { useNoticias } from '../hooks/useNoticias';
import NewsCard from '../components/NewsCard';

function Dashboard() {
    const { noticias, loading, error, loadNews } = useNoticias();
    const [activeMethod, setActiveMethod] = useState('html'); // Estado para saber cuál está activo

    const handleMethodChange = (method) => {
        setActiveMethod(method);
        loadNews(method);
    };

    if (loading) return <div className="loading">Cargando señales...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="dashboard-container"> {/* Añadido container para márgenes */}

            <header>
                <h1>Observatorio de Señales</h1>
                <p>Monitorización en tiempo real de El País</p>
                <div className="filters">
                    <button
                        className={activeMethod === 'html' ? 'active' : ''}
                        onClick={() => handleMethodChange('html')}
                    >
                        Scraper HTML
                    </button>
                    <button
                        className={activeMethod === 'rss' ? 'active' : ''}
                        onClick={() => handleMethodChange('rss')}
                    >
                        Feed RSS
                    </button>
                    <button
                        className={activeMethod === 'browser' ? 'active' : ''}
                        onClick={() => handleMethodChange('browser')}
                    >
                        Navegador Real
                    </button>
                </div>
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