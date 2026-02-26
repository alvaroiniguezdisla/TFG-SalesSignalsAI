import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';
import './ForgotPassword.css';
// Reutilizamos también los estilos de Login.css que son globales para estas vistas
import '../Login/Login.css';

function ForgotPassword() {
    const [email, setEmail] = useState('');
    const [msg, setMsg] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    // Obtenemos la nueva función del Context
    const { resetPassword } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMsg({ type: '', text: '' });

        try {
            await resetPassword(email);
            setMsg({ type: 'success', text: 'Te hemos enviado un enlace de recuperación. Revisa tu bandeja de entrada.' });
        } catch (error) {
            setMsg({ type: 'error', text: 'Error al solicitar el cambio: ' + error.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Recuperar Contraseña</h2>
                <p>Introduce tu correo electrónico para recibir un enlace de recuperación</p>

                {msg.text && (
                    <div className={msg.type === 'error' ? 'error-message' : 'success-message'}>
                        {msg.text}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label>Correo Electrónico</label>
                        <input
                            type="email"
                            placeholder="tu@email.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? 'Enviando...' : 'Enviar Enlace'}
                    </button>
                </form>

                <div className="auth-link">
                    ¿Te has acordado? <Link to="/login">Inicia sesión aquí</Link>
                </div>
            </div>
        </div>
    );
}

export default ForgotPassword;
