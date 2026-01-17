import { useState } from 'react';
import useNoticias from '../hooks/useNoticias';
import NewsCard from '../components/NewsCard';

function Dashboard() {
    const { noticias, loading, error, forceRefresh} = useNoticias();

    const handleRefresh = () => {
        forceRefresh();
    }

    if (loading) return <div className="loading">Cargando señales de la BD...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="dashboard-container"> {/* Añadido container para márgenes */}

            <header>
                <h1>Observatorio de Señales</h1>    
                <p>Monitorización Inteligente de Oportunidades</p>

                <div className="filters">
                    <button onClick={handleRefresh}>Refrescar datos</button>
                </div>
            </header>

            <div className="news-grid">
                {noticias.length > 0 ? (
                    noticias.map((noticia, index) => (
                        <NewsCard key={index} noticia={noticia} />
                    ))
                ) : (
                    <p>No hay noticias disponibles. Ejecuta el pipeline</p>
                )}
            </div>

        </div>
    );
}

export default Dashboard;