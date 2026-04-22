import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import '../Login/Login.css';

function ResetPassword() {
    const [password, setPassword] = useState('');
    const [msg, setMsg] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    const { updatePassword } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMsg({ type: '', text: '' });

        try {
            await updatePassword(password);
            setMsg({ type: 'success', text: '¡Contraseña actualizada correctamente! Redirigiendo...' });

            // Redirigir al dashboard en un par de segundos
            setTimeout(() => {
                navigate('/');
            }, 2000);

        } catch (error) {
            setMsg({ type: 'error', text: 'Error al actualizar la contraseña: ' + error.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Establecer nueva contraseña</h2>
                <p>Escribe tu nueva contraseña segura a continuación</p>

                {msg.text && (
                    <div className={msg.type === 'error' ? 'error-message' : 'success-message'}>
                        {msg.text}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label>Nueva Contraseña</label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            minLength={6}
                        />
                    </div>
                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? 'Actualizando...' : 'Actualizar Contraseña'}
                    </button>
                </form>

                <div className="auth-link">
                    <Link to="/login">Volver a inicio de sesión</Link>
                </div>
            </div>
        </div>
    );
}

export default ResetPassword;
