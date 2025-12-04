import { useNoticias } from '../hooks/useNoticias'; 
import NewsCard from '../components/NewsCard';

function Dashboard() {
    // Usamos el Custom Hook: Lógica separada de la Vista
    const { noticias, loading, error, loadNews } = useNoticias();

    if (loading) return <div className="loading">Cargando señales...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="dashboard">

            <header>
                <h1>Observatorio de Señales</h1>
                <p>Monitorización en tiempo real de El País</p>
                <div className="filters">
                    <button onClick={() => loadNews('html')}>Scraper HTML</button>
                    <button onClick={() => loadNews('rss')}>Feed RSS</button>
                    <button onClick={() => loadNews('browser')}>Navegador Real</button>
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