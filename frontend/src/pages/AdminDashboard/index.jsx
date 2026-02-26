import { useState, useEffect } from 'react';
import { supabase } from '../../supabase/client';
import { useAuth } from '../../context/AuthContext';
import Spinner from '../../components/Spinner';
import './AdminDashboard.css';

function AdminDashboard() {
    const { profile } = useAuth();
    const [config, setConfig] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState({ text: '', type: '' });

    // Estado para el formulario de nueva fuente
    const [showAddForm, setShowAddForm] = useState(false);
    const [newSource, setNewSource] = useState({ name: '', url: '', scraper_url: '', type: 'rss' });

    useEffect(() => {
        fetchConfig();
    }, []);

    const fetchConfig = async () => {
        try {
            setLoading(true);
            const { data, error } = await supabase
                .from('app_config')
                .select('*')
                .eq('id', 1)
                .single();

            if (error) throw error;
            setConfig(data);
        } catch (error) {
            console.error('Error cargando configuración:', error);
            setMessage({ text: 'Error al cargar la configuración de la base de datos.', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            setMessage({ text: '', type: '' });

            // Usamos updated_at para forzar la validez
            const configToSave = {
                ...config,
                updated_at: new Date().toISOString()
            };

            const { error } = await supabase
                .from('app_config')
                .update(configToSave)
                .eq('id', 1);

            if (error) throw error;

            setMessage({ text: 'Configuración global guardada correctamente.', type: 'success' });
            setTimeout(() => setMessage({ text: '', type: '' }), 3000);

        } catch (error) {
            console.error('Error guardando configuración:', error);
            setMessage({ text: 'Error al guardar. Verifica que tienes permisos de Administrador.', type: 'error' });
        } finally {
            setSaving(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type } = e.target;
        setConfig(prev => ({
            ...prev,
            [name]: type === 'number' ? Number(value) : value
        }));
    };

    // --- LÓGICA DE FUENTES RSS ---

    const handleRemoveSource = (indexToRemove) => {
        if (!window.confirm('¿Seguro que quieres eliminar esta fuente de noticias?')) return;

        setConfig(prev => ({
            ...prev,
            rss_sources: prev.rss_sources.filter((_, idx) => idx !== indexToRemove)
        }));
    };

    const handleAddSource = () => {
        if (!newSource.name || !newSource.url) {
            setMessage({ text: 'El nombre y la URL principal son obligatorios.', type: 'error' });
            return;
        }

        setConfig(prev => ({
            ...prev,
            rss_sources: [...prev.rss_sources, newSource]
        }));

        setNewSource({ name: '', url: '', scraper_url: '', type: 'rss' });
        setShowAddForm(false);
    };

    if (loading) return <Spinner message="Cargando configuración global..." />;
    if (!config) return <div className="error-message">No se pudo cargar la configuración.</div>;

    return (
        <div className="admin-container">
            <header className="admin-header">
                <h1>Panel de Control del Sistema</h1>
                <p>Configuración global de la IA, Deduplicación y Motor de Scraping.</p>
            </header>

            {message.text && (
                <div className={message.type === 'error' ? 'error-message' : 'success-message'}>
                    {message.text}
                </div>
            )}

            <div className="admin-grid">
                {/* COLUMNA IZQUIERDA: Variables Globales */}
                <div className="admin-section">
                    <h2>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                        Parámetros Core
                    </h2>

                    <div className="config-form">
                        <div className="form-group">
                            <label>Modelo de Inteligencia Artificial (Ollama)</label>
                            <input
                                type="text"
                                name="ollama_model"
                                value={config.ollama_model}
                                onChange={handleInputChange}
                                placeholder="Ej: llama3.1"
                            />
                        </div>

                        <div className="form-group">
                            <label>Umbral de Similitud (Deduplicación)</label>
                            <input
                                type="number"
                                step="0.01"
                                min="0"
                                max="1"
                                name="umbral_similitud"
                                value={config.umbral_similitud}
                                onChange={handleInputChange}
                            />
                            <small style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>Rango: 0.0 - 1.0 (Ej: 0.85 significa 85% de exactitud requerida para fusionar)</small>
                        </div>

                        <div className="form-group">
                            <label>Límite correos simultáneos</label>
                            <input
                                type="number"
                                name="max_emails_ejecucion"
                                value={config.max_emails_ejecucion}
                                onChange={handleInputChange}
                            />
                        </div>

                        <div className="form-group">
                            <label>Delay entre correos (segundos)</label>
                            <input
                                type="number"
                                name="delay_entre_emails"
                                value={config.delay_entre_emails}
                                onChange={handleInputChange}
                            />
                            <small style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>Previene que Gmail bloquee la cuenta por SPAM.</small>
                        </div>

                    </div>
                </div>

                {/* COLUMNA DERECHA: Web Scraping */}
                <div className="admin-section">
                    <h2>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12h20"></path><path d="M12 2v20"></path><path d="m4.93 4.93 14.14 14.14"></path><path d="m19.07 4.93-14.14 14.14"></path></svg>
                        Fuentes de Extracción (Periódicos)
                    </h2>

                    <div className="sources-list">
                        {config.rss_sources.map((source, idx) => (
                            <div key={idx} className="source-item">
                                <div className="source-info">
                                    <h3>{source.name}</h3>
                                    <p title={source.url}>{source.url.substring(0, 45)}...</p>
                                    <div className="source-badges">
                                        <span className="source-badge">{source.type}</span>
                                        {source.scraper_url && <span className="source-badge">Fallback UI</span>}
                                    </div>
                                </div>
                                <button className="delete-btn" onClick={() => handleRemoveSource(idx)} title="Eliminar fuente">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                                </button>
                            </div>
                        ))}
                    </div>

                    {!showAddForm ? (
                        <button className="btn-add" onClick={() => setShowAddForm(true)}>
                            + Añadir Periodico o Fuente
                        </button>
                    ) : (
                        <div className="add-source-form">
                            <div className="form-group">
                                <label>Nombre Comercial</label>
                                <input
                                    type="text"
                                    placeholder="Ej: Expansión (Empresas)"
                                    value={newSource.name}
                                    onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label>URL Principal (Feed/Web)</label>
                                <input
                                    type="url"
                                    placeholder="https://..."
                                    value={newSource.url}
                                    onChange={(e) => setNewSource({ ...newSource, url: e.target.value })}
                                />
                            </div>
                            <div className="form-group full-width">
                                <label>URL de Respaldo (Browser Fallback) - Opcional</label>
                                <input
                                    type="url"
                                    placeholder="https://..."
                                    value={newSource.scraper_url}
                                    onChange={(e) => setNewSource({ ...newSource, scraper_url: e.target.value })}
                                />
                            </div>
                            <button className="btn-secondary" onClick={() => setShowAddForm(false)}>Cancelar</button>
                            <button className="btn-primary" onClick={handleAddSource}>Integrar Fuente</button>
                        </div>
                    )}
                </div>

                <div className="save-section">
                    <button className="btn-primary" onClick={handleSave} disabled={saving} style={{ width: 'auto' }}>
                        {saving ? 'Guardando en Base de Datos...' : 'Guardar y Desplegar Cambios'}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default AdminDashboard;
