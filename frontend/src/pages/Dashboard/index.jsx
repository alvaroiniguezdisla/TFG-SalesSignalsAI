import { useState, useEffect } from 'react';
import useNoticias from '../../hooks/useNoticias';
import NewsCard from '../../components/NewsCard';
import './Dashboard.css';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Spinner from '../../components/Spinner';


function Dashboard() {
    const { noticias, loading, error, forceRefresh } = useNoticias();
    const { profile } = useAuth();
    const [viewMode, setViewMode] = useState(() => sessionStorage.getItem('dashboard_viewMode') || 'preferences');
    const [sortMode, setSortMode] = useState(() => sessionStorage.getItem('dashboard_sortMode') || 'relevance');
    const [hideNoise, setHideNoise] = useState(() => JSON.parse(sessionStorage.getItem('dashboard_hideNoise') ?? 'false'));

    const [searchTerm, setSearchTerm] = useState(() => sessionStorage.getItem('dashboard_searchTerm') || '');
    const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('dashboard_selectedCompany') || '');
    const [selectedCategory, setSelectedCategory] = useState(() => sessionStorage.getItem('dashboard_selectedCategory') || '');
    const [selectedProduct, setSelectedProduct] = useState(() => sessionStorage.getItem('dashboard_selectedProduct') || '');

    const uniqueCompanies = [...new Set((noticias || []).flatMap(n => n.empresas_clave_ia || []))].filter(Boolean).sort();
    const uniqueCategories = [...new Set((noticias || []).map(n => n.categoria_ia))].filter(Boolean).sort();
    const uniqueProducts = [...new Set((noticias || []).map(n => n.categoria_producto_ia))].filter(n => n && n !== 'Otros / No Aplica').sort();

    useEffect(() => {
        sessionStorage.setItem('dashboard_viewMode', viewMode);
        sessionStorage.setItem('dashboard_sortMode', sortMode);
        sessionStorage.setItem('dashboard_hideNoise', JSON.stringify(hideNoise));
        sessionStorage.setItem('dashboard_searchTerm', searchTerm);
        sessionStorage.setItem('dashboard_selectedCompany', selectedCompany);
        sessionStorage.setItem('dashboard_selectedCategory', selectedCategory);
        sessionStorage.setItem('dashboard_selectedProduct', selectedProduct);
    }, [viewMode, sortMode, hideNoise, searchTerm, selectedCompany, selectedCategory, selectedProduct]);
    const handleRefresh = () => {
        forceRefresh();
    }

    // Lógica de filtrado combinado
    const filteredNoticias = (noticias || []).filter(noticia => {
        if (viewMode === 'preferences') {
            if (!profile) return false;
            const userCompanies = profile.favorite_companies || [];
            const userInterests = profile.favorite_categories || [];

            const newsCompanies = noticia.empresas_clave_ia || [];
            const matchesCompany = userCompanies.some(userCo =>
                newsCompanies.some(newsCo => newsCo.toLowerCase().includes(userCo.toLowerCase()))
            );

            const newsSignal = noticia.categoria_ia || "";
            const newsProduct = noticia.categoria_producto_ia || "";
            const matchesInterest = userInterests.some(interest => {
                const interestLower = interest.toLowerCase();
                return newsSignal.toLowerCase().includes(interestLower) ||
                    newsProduct.toLowerCase().includes(interestLower);
            });

            if (!matchesCompany && !matchesInterest) return false;
        }

        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            const matchTitle = noticia.titulo?.toLowerCase().includes(term);
            const matchSummary = (noticia.resumen_comercial_ia || noticia.resumen || '').toLowerCase().includes(term);
            if (!matchTitle && !matchSummary) return false;
        }

        if (selectedCompany && !(noticia.empresas_clave_ia || []).includes(selectedCompany)) return false;
        if (selectedCategory && noticia.categoria_ia !== selectedCategory) return false;
        if (selectedProduct && noticia.categoria_producto_ia !== selectedProduct) return false;

        return true;
    });

    const noiseFiltered = hideNoise
        ? filteredNoticias.filter(n => (n.relevancia_ia || 0) >= 20)
        : filteredNoticias;

    const sortedNoticias = [...noiseFiltered].sort((a, b) => {
        if (sortMode === 'relevance') {
            return (b.relevancia_ia || 0) - (a.relevancia_ia || 0);
        }
        return new Date(b.scraped_at || 0) - new Date(a.scraped_at || 0);
    });

    const newHighPriority = (noticias || []).filter(n => {
        const isRecent = (new Date() - new Date(n.scraped_at)) < 24 * 60 * 60 * 1000;
        return isRecent && (n.relevancia_ia || 0) >= 70;
    }).length;

    if (loading) return <Spinner message="Sincronizando señales..." />;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="header-top">
                    <div>
                        <h1>
                            Observatorio de Señales
                            {newHighPriority > 0 && (
                                <span className="notification-badge">{newHighPriority} nuevas</span>
                            )}
                        </h1>
                        <p>Monitorización Inteligente de Oportunidades</p>
                    </div>

                    <Link to="/profile" className="profile-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                    </Link>
                </div>

                <div className="filters-section">
                    <input
                        type="text"
                        placeholder="Buscar señales por título o resumen..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                    />

                    <div className="filters-row">
                        <select value={viewMode} onChange={(e) => setViewMode(e.target.value)} className="filter-select">
                            <option value="all">Todas las señales</option>
                            <option value="preferences">Mis preferencias</option>
                        </select>
                        <select value={sortMode} onChange={(e) => setSortMode(e.target.value)} className="filter-select">
                            <option value="relevance">Más relevantes</option>
                            <option value="date">Más recientes</option>
                        </select>
                        <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="filter-select">
                            <option value="">Categoría: Todas</option>
                            {uniqueCategories.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                        <select value={selectedProduct} onChange={(e) => setSelectedProduct(e.target.value)} className="filter-select">
                            <option value="">Producto: Todos</option>
                            {uniqueProducts.map(p => <option key={p} value={p}>{p}</option>)}
                        </select>
                        <select value={selectedCompany} onChange={(e) => setSelectedCompany(e.target.value)} className="filter-select">
                            <option value="">Empresa: Todas</option>
                            {uniqueCompanies.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                    </div>

                    <div className="filters-row">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={hideNoise}
                                onChange={(e) => setHideNoise(e.target.checked)}
                            />
                            Ocultar ruido
                        </label>
                        <button onClick={handleRefresh} className="btn-refresh">Refrescar</button>
                        {(selectedCategory || selectedProduct || selectedCompany || searchTerm) && (
                            <button
                                onClick={() => {
                                    setSearchTerm(''); setSelectedCategory(''); setSelectedProduct(''); setSelectedCompany('');
                                }}
                                className="btn-clear"
                            >
                                Limpiar filtros
                            </button>
                        )}
                    </div>
                </div>
            </header>

            <div className="news-grid">
                {sortedNoticias.length > 0 ? (
                    sortedNoticias.map((noticia, index) => (
                        <NewsCard key={index} noticia={noticia} userCompanies={profile?.favorite_companies || []} />
                    ))
                ) : (
                    <p>No hay noticias disponibles. Ejecuta el pipeline</p>
                )}
            </div>

        </div>
    );
}

export default Dashboard;