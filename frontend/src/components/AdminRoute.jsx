import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Spinner from './Spinner';

const AdminRoute = ({ children }) => {
    const { user, profile, loading, profileResolved } = useAuth();

    if (loading || (user && !profileResolved)) {
        return <Spinner message="Verificando permisos de administrador..." />;
    }

    if (!user) return <Navigate to="/login" />;

    // Solo permitir acceso si el usuario tiene el rol de admin
    if (profile?.role !== 'admin') {
        return <Navigate to="/" />; // Redirigir al dashboard normal si no es admin
    }

    return children;
};

export default AdminRoute;
