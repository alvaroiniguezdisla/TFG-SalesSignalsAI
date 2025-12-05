import { BrowserRouter, Routes, Route, Navigate} from 'react-router-dom';
import Dashboard from '../pages/Dashboard';

export const AppRouter = () => {
    return (
        <BrowserRouter>
            <Routes>
                {/* Si entra en la raíz, lo mandamos a /noticias*/}
                <Route path="/" element={<Navigate to="/noticias" replace />} />

                {/* Aquí pintamos el dashboard */}
                <Route path="/noticias" element={<Dashboard />} />

                {/* Si pone otra ruta que no existe, lo mandamos a /noticias */}
                <Route path="*" element={<Navigate to="/noticias" replace />} />
            </Routes>
        </BrowserRouter>
    )
}