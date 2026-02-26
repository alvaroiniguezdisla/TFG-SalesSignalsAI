import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';
import AdminRoute from '../components/AdminRoute';

import Dashboard from '../pages/Dashboard';
import NewsDetail from '../pages/NewsDetail';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Profile from '../pages/Profile';
import AdminDashboard from '../pages/AdminDashboard';
import ForgotPassword from '../pages/ForgotPassword';
import ResetPassword from '../pages/ResetPassword';


function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Rutas publicas*/}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/actualizar-contrasena" element={<ResetPassword />} />

                {/* Rutas privadas*/}
                <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="/noticia/:id" element={<ProtectedRoute><NewsDetail /></ProtectedRoute>} />
                <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

                {/* Rutas exclusivas de Administrador */}
                <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />

            </Routes>
        </BrowserRouter>
    )
}

export default AppRouter;