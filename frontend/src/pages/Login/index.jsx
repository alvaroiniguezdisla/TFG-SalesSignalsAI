import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import './Login.css';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errorMsg, setErrorMsg] = useState('');
    const [loading, setLoading] = useState(false);

    const { signIn } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrorMsg('');

        try {
            // Intentamos entrar con Supabase
            await signIn(email, password);

            // Si todo va bien, nos vamos al Dashboard
            navigate('/');
        } catch (error) {
            setErrorMsg('Error al iniciar sesion: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Bienvenido de nuevo</h2>
                <p>Introduce tus credenciales para acceder</p>
                {errorMsg && <div className="error-message">{errorMsg}</div>}
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
                    <div className="form-group">
                        <label>Contraseña</label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? 'Entrando...' : 'Iniciar Sesión'}
                    </button>
                </form>
                <div className="auth-link">
                    ¿No tienes cuenta? <Link to="/register">Regístrate aquí</Link>
                </div>
                <div className="auth-link" style={{ marginTop: '10px' }}>
                    ¿Has olvidado tu contraseña? <Link to="/forgot-password">Recupérala aquí</Link>
                </div>
            </div>
        </div>
    );
}
export default Login;
