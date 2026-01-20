import { useState } from 'react';
import useNoticias from '../../hooks/useNoticias';
import NewsCard from '../../components/NewsCard';
import './Dashboard.css';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';


function Dashboard() {
    const { noticias, loading, error, forceRefresh } = useNoticias();
    const { profile } = useAuth();
    const [viewMode, setViewMode] = useState('all'); // 'all' | 'preferences'

    const handleRefresh = () => {
        forceRefresh();
    }

    // Lógica de filtrado
    const filteredNoticias = viewMode === 'all'
        ? noticias
        : noticias.filter(noticia => {
            const companies_user= profile?.favorite_companies || [];
            const categories_user=profile?.favorite_categories || [];

            // --- 1.  FILTRO DE EMPRESAS ---
            const tagsDeNoticia=noticia.empresas_clave_ia || [];
            const matchCompany = companies_user.some(miFavorita => {
                // Miramos si alguna  empresa favorita del user está incluída en los tags de la noticia
                return tagsDeNoticia.some(tagIA => 
                    tagIA.toLowerCase().includes(miFavorita.toLowerCase())
                );
            });

            // --- 2.  FILTRO DE CATEGORIAS ---
            const tagsDeCategoria=noticia.categoria_ia || [];
            const matchCategory = categories_user.some(miFavorita => {
                // Miramos si alguna  categoria favorita del user está incluída en los tags de la noticia
                return tagsDeCategoria.some(tagIA => 
                    tagIA.toLowerCase().includes(miFavorita.toLowerCase())
                );
            });
            return matchCompany || matchCategory;
        });

    if (loading) return <div className="loading">Cargando señales de la BD...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="header-top">
                    <div>
                        <h1>Observatorio de Señales</h1>
                        <p>Monitorización Inteligente de Oportunidades</p>
                    </div>

                    {/* ICONO DE PERFIL */}
                    <Link to="/profile" className="profile-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                    </Link>
                </div>

                <div className="filters">
                    <select
                        value={viewMode}
                        onChange={(e) => setViewMode(e.target.value)}
                        className="view-selector"
                    >
                        <option value="all">Todas las noticias</option>
                        <option value="preferences">Mis preferencias</option>
                    </select>
                    <button onClick={handleRefresh} className="refresh-btn">Refrescar datos</button>
                </div>
            </header>

            <div className="news-grid">
                {filteredNoticias.length > 0 ? (
                    filteredNoticias.map((noticia, index) => (
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