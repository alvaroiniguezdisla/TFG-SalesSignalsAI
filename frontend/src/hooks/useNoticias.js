import { useState, useEffect, useCallback } from 'react';
import { getNoticias } from '../services/api';

/**
 * Custom Hook para gestionar la lógica de noticias.
 * @returns {Object} { noticias, loading, error, loadNews }
 */
function useNoticias() {

    const [noticias, setNoticias] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadNews = useCallback(async (metodo = 'html') => {
        try {
            setLoading(true);
            setError(null); // Limpiamos errores previos
            const data = await getNoticias(metodo);
            setNoticias(data);
        } catch (err) {
            setError("No se pudieron cargar las noticias. ¿Está el backend encendido?");
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Carga inicial
    useEffect(() => {
        loadNews();
    }, [loadNews]);

    return { noticias, loading, error, loadNews };
}

export default useNoticias;
