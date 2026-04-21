import { useState, useEffect, useCallback } from 'react';
import { getNoticias, refreshNews } from '../services/api';


function useNoticias() {

    const [noticias, setNoticias] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadNews = useCallback(async () => {
        try {
            setLoading(true);
            setError(null); // Limpiamos errores previos
            const data = await getNoticias();
            setNoticias(data);
        } catch (err) {
            setError("No se pudieron cargar las noticias. ¿Está el backend encendido?");
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    const forceRefresh = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            //1. LLamamos al backen para que haga la ingesta de nocticias
            await refreshNews();

            //2. Volvemos a cargar los datos de la BD
            await loadNews();

        } catch (err) {
            console.error(err);
            setError("Error al refrescar las noticias");
            setLoading(false);
        }
    }, [loadNews]);




    // Carga inicial
    useEffect(() => {
        loadNews();
    }, [loadNews]);

    return { noticias, loading, error, loadNews, forceRefresh };
}

export default useNoticias;
