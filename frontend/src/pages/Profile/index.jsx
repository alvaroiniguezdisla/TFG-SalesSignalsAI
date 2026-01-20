import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import './Profile.css';

function Profile() {
    // 1. Usamos el contexto
    const { user, profile, signOut, updateProfile } = useAuth();

    // 2. Estados locales para la edición
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        favorite_companies: [],
        favorite_categories: []
    });
    const [newCompany, setNewCompany] = useState('');
    const [newCategory, setNewCategory] = useState('');

    // Cargar datos del perfil en el formulario cuando llegan
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

    // Manejador de cambios en los inputs
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    // Guardar cambios
    const handleSave = async () => {
        try {
            await updateProfile(formData);
            setIsEditing(false);
            alert("Perfil actualizado correctamente");
        } catch (error) {
            alert("Error al actualizar: " + error.message);
        }
    };

    // Añadir empresa
    const handleAddCompany = () => {
        if (newCompany.trim() && !formData.favorite_companies.includes(newCompany.trim())) {
            setFormData({
                ...formData,
                favorite_companies: [...formData.favorite_companies, newCompany.trim()]
            });
            setNewCompany('');
        }
    };

    // Eliminar empresa
    const handleRemoveCompany = (company) => {
        setFormData({
            ...formData,
            favorite_companies: formData.favorite_companies.filter(c => c !== company)
        });
    };

    // Añadir categoría
    const handleAddCategory = () => {
        if (newCategory.trim() && !formData.favorite_categories.includes(newCategory.trim())) {
            setFormData({
                ...formData,
                favorite_categories: [...formData.favorite_categories, newCategory.trim()]
            });
            setNewCategory('');
        }
    };

    // Eliminar categoría
    const handleRemoveCategory = (category) => {
        setFormData({
            ...formData,
            favorite_categories: formData.favorite_categories.filter(c => c !== category)
        });
    };

    return (
        <div className="profile-container">
            <h1>Mi Perfil</h1>

            <div className="profile-card">
                {/* SECCIÓN 1: Datos de la Cuenta (Vienen de auth.users / user) */}
                <div className="section">
                    <h3>Cuenta</h3>
                    <p><strong>Email:</strong> {user?.email}</p>
                    <p><strong>ID:</strong> {user?.id}</p>
                </div>
                <hr />

                {/* SECCIÓN 2: Datos del Perfil (Editables) */}
                <div className="section">
                    <div className="section-header">
                        <h3>Datos Personales</h3>
                        {!isEditing && (
                            <button onClick={() => setIsEditing(true)} className="edit-btn">
                                Editar
                            </button>
                        )}
                    </div>

                    {isEditing ? (
                        <div className="edit-form">
                            <div className="form-group">
                                <label>Nombre</label>
                                <input
                                    type="text"
                                    name="first_name"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-group">
                                <label>Apellido</label>
                                <input
                                    type="text"
                                    name="last_name"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="edit-actions">
                                <button onClick={handleSave} className="save-btn">Guardar</button>
                                <button onClick={() => setIsEditing(false)} className="cancel-btn">Cancelar</button>
                            </div>
                        </div>
                    ) : (
                        <div className="view-mode">
                            <p><strong>Nombre:</strong> {profile?.first_name || 'Sin nombre'}</p>
                            <p><strong>Apellido:</strong> {profile?.last_name || 'Sin apellido'}</p>
                        </div>
                    )}
                </div>
                <hr />

                {/* SECCIÓN 3: PREFERENCIAS */}
                <div className="section">
                    <h3>Mis preferencias</h3>

                    {/* EMPRESAS FAVORITAS */}
                    <div className="preference-group">
                        <label>Empresas Favoritas</label>
                        <div className="add-row">
                            <input
                                type="text"
                                placeholder="Ej: Iberdrola"
                                value={newCompany}
                                onChange={(e) => setNewCompany(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleAddCompany()}
                            />
                            <button type="button" onClick={handleAddCompany} className="add-btn">Añadir</button>
                        </div>
                        <div className="tags-container">
                            {formData.favorite_companies.map((company, index) => (
                                <span key={index} className="tag">
                                    {company}
                                    <button onClick={() => handleRemoveCompany(company)} className="tag-remove">✕</button>
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* CATEGORÍAS FAVORITAS */}
                    <div className="preference-group">
                        <label>Categorías Favoritas</label>
                        <div className="add-row">
                            <input
                                type="text"
                                placeholder="Ej: Energía"
                                value={newCategory}
                                onChange={(e) => setNewCategory(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleAddCategory()}
                            />
                            <button type="button" onClick={handleAddCategory} className="add-btn">Añadir</button>
                        </div>
                        <div className="tags-container">
                            {formData.favorite_categories.map((category, index) => (
                                <span key={index} className="tag">
                                    {category}
                                    <button onClick={() => handleRemoveCategory(category)} className="tag-remove">✕</button>
                                </span>
                            ))}
                        </div>
                    </div>
                </div>


                <div className="section-actions">
                    <button onClick={async () => {
                        try {
                            await updateProfile(formData);
                            alert("Preferencias guardadas correctamente");
                        } catch (error) {
                            alert("Error al guardar: " + error.message);
                        }
                    }} className="save-prefs-btn">
                        Guardar Preferencias
                    </button>
                </div>
                <hr />

                <div className="footer-actions">
                    <button onClick={signOut} className="logout-btn">
                        Cerrar Sesión
                    </button>
                </div>
            </div>
        </div >
    )
}

export default Profile;