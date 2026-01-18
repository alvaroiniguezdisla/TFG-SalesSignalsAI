import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import NewsDetail from '../pages/NewsDetail'; 

function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Si entra en la raíz, lo mandamos a /noticias*/}
                <Route path="/" element={<Dashboard />} />
                <Route path="/noticia/:id" element={<NewsDetail />} />

            </Routes>
        </BrowserRouter>
    )
}

export default AppRouter;