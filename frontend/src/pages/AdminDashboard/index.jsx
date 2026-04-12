import { useState, useEffect } from 'react';
import { supabase } from '../../supabase/client';
import { useAuth } from '../../context/AuthContext';
import Spinner from '../../components/Spinner';
import { API_URL } from '../../services/api';
import './AdminDashboard.css';

function AdminDashboard() {
    const { profile } = useAuth();
    const [config, setConfig] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState({ text: '', type: '' });

    // --- Estados de métricas y usuarios ---
    const [metrics, setMetrics] = useState(null);
    const [users, setUsers] = useState([]);
    const [loadingUsers, setLoadingUsers] = useState(false);

    // --- Estado para Crear Usuario ---
    const [showAddUser, setShowAddUser] = useState(false);
    const [newUser, setNewUser] = useState({ email: '', password: '', role: 'user' });

    // Estado para el formulario de nueva fuente
    const [showAddForm, setShowAddForm] = useState(false);
    const [newSource, setNewSource] = useState({ name: '', url: '', scraper_url: '', type: 'rss' });

    useEffect(() => {
        const loadAllAdminData = async () => {
            setLoading(true);
            await Promise.all([
                fetchConfig(),
                fetchMetrics(),
                fetchUsers()
            ]);
            setLoading(false);
        };
        loadAllAdminData();
    }, []);

    const fetchConfig = async () => {
        try {
            const response = await fetch(`${API_URL}/api/admin/config`);
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            const data = await response.json();
            setConfig(data);
        } catch (error) {
            console.error('Error cargando configuración:', error);
            setMessage({ text: 'Error al cargar la configuración de la base de datos (Backend inalcanzable u otro).', type: 'error' });
        }
    };

    const fetchMetrics = async () => {
        try {
            const response = await fetch(`${API_URL}/api/admin/metrics`);
            if (!response.ok) throw new Error('Error fetcheando métricas');
            const data = await response.json();
            setMetrics(data);
        } catch (error) {
            console.error('API Error (Métricas):', error);
        }
    };

    const fetchUsers = async () => {
        try {
            const response = await fetch(`${API_URL}/api/admin/users`);
            if (!response.ok) throw new Error('Error fetcheando usuarios');
            const data = await response.json();
            setUsers(data);
        } catch (error) {
            console.error('API Error (Usuarios):', error);
        }
    };

    const handleRoleChange = async (userId, newRole) => {
        try {
            setLoadingUsers(true);
            const response = await fetch(`${API_URL}/api/admin/users/${userId}/role`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: newRole })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Error cambiando rol');
            }

            setMessage({ text: 'Rol de usuario actualizado correctamente.', type: 'success' });
            setTimeout(() => setMessage({ text: '', type: '' }), 3000);

            // Refrescar lista de usuarios locales
            setUsers(prevUsers =>
                prevUsers.map(u => u.id === userId ? { ...u, role: newRole } : u)
            );
        } catch (error) {
            console.error('Error al cambiar rol:', error);
            setMessage({ text: error.message, type: 'error' });
        } finally {
            setLoadingUsers(false);
        }
    };

    const handleDeleteUser = async (userId, userEmail) => {
        if (!window.confirm(`ADVERTENCIA DE SEGURIDAD\n\nEstá a punto de eliminar permanentemente al usuario:\n${userEmail}\n\nEsta acción es irreversible y borrará todos sus datos asociados. ¿Desea proceder?`)) {
            return;
        }

        try {
            setLoadingUsers(true);
            const response = await fetch(`${API_URL}/api/admin/users/${userId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Error eliminando usuario');
            }

            setMessage({ text: 'Usuario eliminado permanentemente.', type: 'success' });
            setTimeout(() => setMessage({ text: '', type: '' }), 3000);

            setUsers(prevUsers => prevUsers.filter(u => u.id !== userId));
            fetchMetrics(); // Refrescar métricas visuales
        } catch (error) {
            console.error('Error al eliminar usuario:', error);
            setMessage({ text: error.message, type: 'error' });
        } finally {
            setLoadingUsers(false);
        }
    };

    const handleCreateUser = async () => {
        if (!newUser.email || !newUser.password) {
            setMessage({ text: 'Email y contraseña son obligatorios.', type: 'error' });
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(newUser.email)) {
            setMessage({ text: 'Por favor, introduce un formato de email válido (ej: usuario@dominio.com).', type: 'error' });
            return;
        }

        if (newUser.password.length < 6) {
            setMessage({ text: 'La contraseña debe tener al menos 6 caracteres.', type: 'error' });
            return;
        }

        try {
            setLoadingUsers(true);
            const response = await fetch(`${API_URL}/api/admin/users`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newUser)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Error creando usuario');
            }

            const responseData = await response.json();

            setMessage({ text: `Usuario ${newUser.email} creado exitosamente.`, type: 'success' });
            setTimeout(() => setMessage({ text: '', type: '' }), 4000);

            // Refrescar lista de usuarios locales para que aparezca INSTANTÁNEAMENTE
            const basicName = newUser.email.split('@')[0];
            setUsers(prevUsers => [...prevUsers, {
                id: responseData.user.id,
                email: newUser.email,
                role: newUser.role,
                first_name: basicName,
                created_at: new Date().toISOString()
            }]);

            setNewUser({ email: '', password: '', role: 'user' });
            setShowAddUser(false);

            // Recargar métricas visuales
            fetchMetrics();
        } catch (error) {
            console.error('Error al crear usuario:', error);
            setMessage({ text: error.message, type: 'error' });
        } finally {
            setLoadingUsers(false);
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

            const response = await fetch(`${API_URL}/api/admin/config`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configToSave)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Error al guardar configuración.');
            }

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

            {/*  MÉTRICAS (KPIs) */}
            {metrics && (
                <div className="metrics-grid">
                    <div className="metric-card">
                        <div className="metric-icon users-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                        </div>
                        <div className="metric-content">
                            <h3>Usuarios Registrados</h3>
                            <p className="metric-value">{metrics.total_users}</p>
                            <p className="metric-subtext">{metrics.active_users_30d} activos (30d)</p>
                        </div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-icon news-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        </div>
                        <div className="metric-content">
                            <h3>Noticias Ingestadas</h3>
                            <p className="metric-value">{metrics.total_news}</p>
                            <p className="metric-subtext">+{metrics.news_7d} (últimos 7 días)</p>
                        </div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-icon feedback-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                        </div>
                        <div className="metric-content">
                            <h3>Interacción (Feedback)</h3>
                            <p className="metric-value">{metrics.total_feedbacks}</p>
                            <p className="metric-subtext">Valoraciones Positivas: {metrics.likes_count} | Negativas: {metrics.dislikes_count}</p>
                        </div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-icon sources-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                        </div>
                        <div className="metric-content">
                            <h3>Fuentes Activas</h3>
                            <p className="metric-value">{metrics.active_sources}</p>
                            <p className="metric-subtext">Periódicos en monitorización</p>
                        </div>
                    </div>
                </div>
            )}

            {/*  GESTIÓN DE USUARIOS */}
            <div className="admin-section full-width-section users-section" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                    <h2 style={{ margin: 0, borderBottom: 'none', paddingBottom: 0 }}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                        Gestión de Usuarios (Control de Acceso)
                    </h2>

                    {!showAddUser && (
                        <button className="btn-add-mini" onClick={() => setShowAddUser(true)}>
                            + Añadir Usuario
                        </button>
                    )}
                </div>

                {showAddUser && (
                    <div className="add-source-form" style={{ marginBottom: '1.5rem' }}>
                        <div className="form-group">
                            <label>Email del nuevo usuario</label>
                            <input
                                type="email"
                                placeholder="ejemplo@ceu.es"
                                value={newUser.email}
                                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label>Contraseña Temporal</label>
                            <input
                                type="password"
                                placeholder="Mínimo 6 caracteres"
                                value={newUser.password}
                                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                            />
                        </div>
                        <div className="form-group full-width">
                            <label>Rol Inicial</label>
                            <select
                                value={newUser.role}
                                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                            >
                                <option value="user">Usuario Estándar (Lectura y Feedback)</option>
                                <option value="admin">Administrador (Acceso Completo)</option>
                            </select>
                        </div>
                        <button className="btn-secondary" onClick={() => setShowAddUser(false)} disabled={loadingUsers}>Cancelar</button>
                        <button className="btn-primary" onClick={handleCreateUser} disabled={loadingUsers}>
                            {loadingUsers ? 'Creando...' : 'Dar de Alta'}
                        </button>
                    </div>
                )}

                <div className="table-responsive">
                    <table className="users-table">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Email</th>
                                <th>Fecha Registro</th>
                                <th>Rol en Plataforma</th>
                                <th style={{ textAlign: 'center' }}>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id}>
                                    <td>
                                        <div className="user-name-cell">
                                            {user.first_name || user.email.split('@')[0]} {user.last_name || ''}
                                            {user.id === profile?.id && <span className="badge-you">Tú</span>}
                                        </div>
                                    </td>
                                    <td>{user.email}</td>
                                    <td>{new Date(user.created_at).toLocaleDateString()}</td>
                                    <td>
                                        <select
                                            className={`role-select ${user.role}`}
                                            value={user.role}
                                            onChange={(e) => handleRoleChange(user.id, e.target.value)}
                                            disabled={loadingUsers || user.id === profile?.id} // Protege auto-quitarse admin
                                        >
                                            <option value="user">Usuario Estándar</option>
                                            <option value="admin">Administrador</option>
                                        </select>
                                    </td>
                                    <td style={{ textAlign: 'center' }}>
                                        <button
                                            className="btn-delete-user"
                                            title="Eliminar usuario definitivamente"
                                            onClick={() => handleDeleteUser(user.id, user.email)}
                                            disabled={loadingUsers || user.id === profile?.id} // Protege borrado propio
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

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

                {/* SECCIÓN INFERIOR: Prompt de Inteligencia Artificial */}
                <div className="admin-section full-width-section">
                    <h2>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                        Instrucciones Base de IA
                    </h2>

                    <div className="prompt-editor-container">
                        <div className="prompt-info-header">
                            <p className="prompt-description">
                                <strong>Configuración de Análisis (Editable):</strong> Define cómo debe actuar la IA, qué reglas de negocio seguir y qué tono utilizar.
                            </p>
                            <button
                                className="btn-outline-danger"
                                onClick={() => {
                                    if (window.confirm('¿Seguro que quieres restaurar el prompt por defecto de fábrica? Perderás los cambios actuales.')) {
                                        setConfig({ ...config, ai_prompt: config.ai_prompt_default });
                                    }
                                }}
                                title="Borra el prompt actual y devuelve el control al código fuente del sistema (Fallback)."
                            >
                                Restaurar Prompt por Defecto
                            </button>
                        </div>

                        <textarea
                            className="prompt-textarea"
                            value={config.ai_prompt || ''}
                            onChange={(e) => setConfig({ ...config, ai_prompt: e.target.value })}
                            placeholder="Escribe aquí las instrucciones de análisis para la IA. Si dejas este campo vacío, se usará el prompt de fábrica del sistema."
                        />

                        <div className="prompt-security-warning">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                            <span><strong>Protección Activa:</strong> El formato de salida JSON y los tipos de datos están sellados por código en el backend y <strong>NO pueden ser alterados</strong> desde este panel. Esto garantiza que la aplicación no sufra caídas por un mal formato.</span>
                        </div>
                    </div>
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
