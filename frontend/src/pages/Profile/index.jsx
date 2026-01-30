import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getCategories } from '../../services/api';
import './Profile.css';

function Profile() {
    const navigate = useNavigate();
    const { user, profile, signOut, updateProfile } = useAuth()
    // Estado de carga y datos
    const [loading, setLoading] = useState(true);
    const [isEditingInfo, setIsEditingInfo] = useState(false);

    // Formulario de Datos Personales
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        favorite_companies: [],
        favorite_categories: []
    });

    // Inputs temporales para añadir tags
    const [newCompany, setNewCompany] = useState('');
    const [selectedSignal, setSelectedSignal] = useState('');
    const [selectedProduct, setSelectedProduct] = useState('');

    // Listas maestras del Backend
    const [availableSignals, setAvailableSignals] = useState([]);
    const [availableProducts, setAvailableProducts] = useState([]);

    // --- CARGA DE DATOS ---
    // 1. Carga Inicial de Categorias (Solo una vez)
    useEffect(() => {
        const loadCategories = async () => {
            setLoading(true);
            try {
                const cats = await getCategories();
                setAvailableSignals(cats.signals || []);
                setAvailableProducts(cats.products || []);
            } catch (err) {
                console.error("Error cargando categorías:", err);
            } finally {
                setLoading(false);
            }
        };
        loadCategories();
    }, []);

    // 2. Sincronización de Perfil (Silenciosa - Sin Loading)
    useEffect(() => {
        if (profile) {
            setFormData({
                first_name: profile.first_name || '',
                last_name: profile.last_name || '',
                favorite_companies: profile.favorite_companies || [],
                favorite_categories: profile.favorite_categories || []
            });
        }
    }, [profile]);

    // --- HANDLERS DATOS PERSONALES ---
    const handleInfoChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const savePersonalInfo = async () => {
        try {
            await updateProfile({
                first_name: formData.first_name,
                last_name: formData.last_name
            });
            setIsEditingInfo(false);
        } catch (error) {
            alert("Error al guardar: " + error.message);
        }
    };

    // --- HANDLERS PREFERENCIAS (Agregación Genérica) ---
    const addItem = (listName, item) => {
        if (!item) return;
        const list = formData[listName];
        if (!list.includes(item)) {
            const newData = { ...formData, [listName]: [...list, item] };
            setFormData(newData);
            // Auto-guardado al añadir preferencia para UX fluida
            updateProfile(newData).catch(e => alert("Error guardando preferencia"));
        }
    };

    const removeItem = (listName, item) => {
        const newData = {
            ...formData,
            [listName]: formData[listName].filter(i => i !== item)
        };
        setFormData(newData);
        updateProfile(newData).catch(e => alert("Error eliminando preferencia"));
    };

    // --- HELPERS VISUALES ---
    const getInitials = () => {
        const f = formData.first_name?.[0] || user?.email?.[0] || '?';
        const l = formData.last_name?.[0] || '';
        return (f + l).toUpperCase();
    };

    // Filtrar mis categorías para mostrar separadas en UI
    const mySignals = formData.favorite_categories.filter(c => availableSignals.includes(c));
    const myProducts = formData.favorite_categories.filter(c => availableProducts.includes(c));
    // Las que no encajan en ninguna (por si acaso cambian las listas backend)
    const myOthers = formData.favorite_categories.filter(c => !availableSignals.includes(c) && !availableProducts.includes(c));

    if (loading) return <div className="loading-screen">Cargando perfil...</div>;

    return (
        <div className="profile-layout">
            <header className="profile-header">
                <button onClick={() => navigate('/')} className="back-link">
                    &larr; Volver al Dashboard
                </button>
                <div className="header-content">
                    <div className="avatar-circle">
                        {getInitials()}
                    </div>
                    <div className="user-headlines">
                        <h1>{formData.first_name} {formData.last_name || ''}</h1>
                        <span className="user-email">{user?.email}</span>
                    </div>
                    <button onClick={signOut} className="logout-btn-header">
                        Cerrar Sesión
                    </button>
                </div>
            </header>

            <main className="profile-grid">

                {/* COLUMNA IZQUIERDA: Configuración y Datos */}
                <div className="profile-col-left">

                    {/* Tarjeta: Datos Personales */}
                    <div className="card profile-card">
                        <div className="card-header">
                            <h2>Información Personal</h2>
                            {!isEditingInfo && (
                                <button onClick={() => setIsEditingInfo(true)} className="btn-icon-edit">
                                    Editar
                                </button>
                            )}
                        </div>

                        <div className="card-body">
                            {isEditingInfo ? (
                                <div className="edit-form">
                                    <div className="form-group">
                                        <label>Nombre</label>
                                        <input
                                            name="first_name"
                                            value={formData.first_name}
                                            onChange={handleInfoChange}
                                            placeholder="Tu nombre"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Apellidos</label>
                                        <input
                                            name="last_name"
                                            value={formData.last_name}
                                            onChange={handleInfoChange}
                                            placeholder="Tus apellidos"
                                        />
                                    </div>
                                    <div className="form-actions">
                                        <button onClick={savePersonalInfo} className="btn-primary">Guardar</button>
                                        <button onClick={() => setIsEditingInfo(false)} className="btn-secondary">Cancelar</button>
                                    </div>
                                </div>
                            ) : (
                                <div className="info-display">
                                    <div className="info-row">
                                        <span className="label">Nombre completo</span>
                                        <span className="value">{formData.first_name} {formData.last_name}</span>
                                    </div>

                                </div>
                            )}
                        </div>
                    </div>

                    {/* Tarjeta: Seguridad */}
                    <div className="card profile-card">
                        <div className="card-header">
                            <h2>Seguridad</h2>
                        </div>
                        <div className="card-body">
                            <div className="info-row">
                                <span className="label">Email asociado</span>
                                <span className="value">{user?.email}</span>
                            </div>
                            <div className="security-actions">
                                <button className="btn-outline-danger" disabled title="Próximamente">
                                    Cambiar Contraseña
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* COLUMNA DERECHA: Preferencias e Inteligencia */}
                <div className="profile-col-right">

                    {/* Preferencias de Negocio (Señales) */}
                    <div className="card preferences-card">
                        <div className="card-header">
                            <h2>Intereses de Negocio</h2>
                            <p className="card-subtitle">Filtra noticias por tipo de señal</p>
                        </div>
                        <div className="card-body">
                            <div className="tags-cloud">
                                {mySignals.map(sig => (
                                    <span key={sig} className="tag-pill signal">
                                        {sig}
                                        <button onClick={() => removeItem('favorite_categories', sig)}>×</button>
                                    </span>
                                ))}
                                {mySignals.length === 0 && <span className="empty-msg">Sin intereses seleccionados</span>}
                            </div>

                            <div className="add-bar">
                                <select
                                    value={selectedSignal}
                                    onChange={(e) => {
                                        addItem('favorite_categories', e.target.value);
                                        setSelectedSignal(''); // Reset inmediato
                                    }}
                                >
                                    <option value="">+ Añadir interés...</option>
                                    {availableSignals
                                        .filter(s => !formData.favorite_categories.includes(s))
                                        .map(s => <option key={s} value={s}>{s}</option>)
                                    }
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Preferencias de Producto */}
                    <div className="card preferences-card">
                        <div className="card-header">
                            <h2>Líneas de Producto</h2>
                            <p className="card-subtitle">Productos HP que gestionas</p>
                        </div>
                        <div className="card-body">
                            <div className="tags-cloud">
                                {myProducts.map(prod => (
                                    <span key={prod} className="tag-pill product">
                                        {prod}
                                        <button onClick={() => removeItem('favorite_categories', prod)}>×</button>
                                    </span>
                                ))}
                                {myProducts.length === 0 && <span className="empty-msg">Sin productos seleccionados</span>}
                            </div>

                            <div className="add-bar">
                                <select
                                    value={selectedProduct}
                                    onChange={(e) => {
                                        addItem('favorite_categories', e.target.value);
                                        setSelectedProduct('');
                                    }}
                                >
                                    <option value="">+ Añadir producto...</option>
                                    {availableProducts
                                        .filter(p => !formData.favorite_categories.includes(p))
                                        .map(p => <option key={p} value={p}>{p}</option>)
                                    }
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Empresas Clave */}
                    <div className="card preferences-card">
                        <div className="card-header">
                            <h2>Empresas Objetivo</h2>
                            <p className="card-subtitle">Seguimiento prioritario</p>
                        </div>
                        <div className="card-body">
                            <div className="tags-cloud">
                                {formData.favorite_companies.map(comp => (
                                    <span key={comp} className="tag-pill company">
                                        {comp}
                                        <button onClick={() => removeItem('favorite_companies', comp)}>×</button>
                                    </span>
                                ))}
                            </div>

                            <div className="add-bar input-group">
                                <input
                                    type="text"
                                    placeholder="Añadir empresa (ej: Telefónica)..."
                                    value={newCompany}
                                    onChange={(e) => setNewCompany(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            addItem('favorite_companies', newCompany);
                                            setNewCompany('');
                                        }
                                    }}
                                />
                                <button
                                    className="btn-add"
                                    onClick={() => {
                                        addItem('favorite_companies', newCompany);
                                        setNewCompany('');
                                    }}
                                >
                                    +
                                </button>
                            </div>
                        </div>
                    </div>

                </div>
            </main>
        </div >
    );
}

export default Profile;