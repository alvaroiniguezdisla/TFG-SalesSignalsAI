import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Spinner from './Spinner';
const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();

    //Si está cargando, mostramos un mensaje
    if (loading) return <Spinner message="Validando sesión..." />

    //Si no hay usuario, lo mandamos a login
    if (!user) return <Navigate to="/login" />;

    //Si hay usuario, mostramos la página
    return children;
};

export default ProtectedRoute;