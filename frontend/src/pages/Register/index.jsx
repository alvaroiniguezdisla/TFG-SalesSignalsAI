import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import '../Login/Login.css';

function Register() {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        first_name: '',
        last_name: ''
    });
    const [errorMsg, setErrorMsg] = useState('');
    const [loading, setLoading] = useState(false);

    const {signUp} = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {

        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };
    const handleSubmit = async (e) =>{
        e.preventDefault();
        setLoading(true);
        setErrorMsg('');

        try{
            await signUp(formData.email, formData.password,{first_name: formData.first_name, last_name: formData.last_name});
            alert('¡Cuenta creada! Revisa tu correo o inicia sesión.');
            navigate('/login');

        }catch(error){
            setErrorMsg('Error al registrarse: ' + error.message);
        }finally{
            setLoading(false);
        }
    }

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Crear cuenta</h2>
                <p>Regístrate para acceder al panel de señales</p>
                {errorMsg && <div className="error-message">{errorMsg}</div>}
                <form onSubmit={handleSubmit} className="auth-form">
                    {/* Nombre y Apellido */}
                    <div className="form-group">
                        <label>Nombre</label>
                        <input name="first_name" type="text" placeholder="Ej: Álvaro" required
                            onChange={handleChange} value={formData.first_name} />
                    </div>
                    <div className="form-group">
                        <label>Apellidos</label>
                        <input name="last_name" type="text" placeholder="Ej: García" required
                            onChange={handleChange} value={formData.last_name} />
                    </div>
                    {/* Email y Password */}
                    <div className="form-group">
                        <label>Correo</label>
                        <input name="email" type="email" placeholder="tu@email.com" required
                            onChange={handleChange} value={formData.email} />
                    </div>
                    <div className="form-group">
                        <label>Contraseña</label>
                        <input name="password" type="password" placeholder="Mínimo 6 caracteres" required
                            onChange={handleChange} value={formData.password} />
                    </div>
                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? 'Creando...' : 'Registrarme'}
                    </button>
                </form>
                <div className="auth-link">
                    ¿Ya tienes cuenta? <Link to="/login">Inicia Sesión</Link>
                </div>
            </div>
        </div>
    );

};

export default Register;
