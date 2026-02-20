import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';

import Dashboard from '../pages/Dashboard';
import NewsDetail from '../pages/NewsDetail'; 
import Login from '../pages/Login';
import Register from '../pages/Register';
import Profile from '../pages/Profile';


function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Rutas publicas*/}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                {/* Rutas privadas*/}
                <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="/noticia/:id" element={<ProtectedRoute><NewsDetail /></ProtectedRoute>} />
                <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

            </Routes>
        </BrowserRouter>
    )
}

export default AppRouter;