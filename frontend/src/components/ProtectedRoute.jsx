import  { Navigate } from 'react-router-dom';
import { useAuth} from '../context/AuthContext';

const ProtectedRoute= ({ children }) => {
    const { user, loading}=useAuth();

    //Si está cargando, mostramos un mensaje
    if (loading) return <div>Cargando...</div>

    //Si no hay usuario, lo mandamos a login
    if (!user) return <Navigate to="/login" />;

    //Si hay usuario, mostramos la página
    return children;
};

export default ProtectedRoute;