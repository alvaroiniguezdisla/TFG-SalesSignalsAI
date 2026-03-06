import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getUserFeedbacks, saveFeedback, removeFeedback } from '../services/feedbackService';

function useFeedback() {
    const { user } = useAuth();
    // Diccionario para acceso asíncrono O(1): { [url_hash]: 'like' | 'dislike' }
    const [feedbacks, setFeedbacks] = useState({});
    const [loading, setLoading] = useState(true);

    // Cargar todos los feedbacks del usuario al montar
    useEffect(() => {
        async function loadFeedbacks() {
            if (!user) {
                setFeedbacks({});
                setLoading(false);
                return;
            }

            try {
                const data = await getUserFeedbacks(user.id);

                // Convertir el array base de datos en diccionario rápido
                const feedbackMap = {};
                data.forEach(item => {
                    feedbackMap[item.noticia_url_hash] = item.feedback;
                });

                setFeedbacks(feedbackMap);
            } catch (err) {
                console.error("Error al cargar feedback de las noticias:", err);
            } finally {
                setLoading(false);
            }
        }

        loadFeedbacks();
    }, [user]);

    /**
     * Hace toggle sobre el feedback de una noticia.
     * Implementa "Optimistic UI": actualiza visualmente la interfaz antes de esperar
     * a que el backend responda, mejorando enormemente la percepción de velocidad.
     */
    const toggleFeedback = useCallback(async (urlHash, type) => {
        if (!user) return; // Protección: solo autenticados

        const currentType = feedbacks[urlHash];
        let newFeedbacks = { ...feedbacks };

        // 1. Lógica del Toggle
        let action = 'none'; // 'insert_update' o 'delete'

        if (currentType === type) {
            // Si pulsa el mismo botón que ya tiene activo, se quita (DELETE)
            action = 'delete';
        } else {
            // Si es diferente o no existía, se sobreescribe/inserta (UPSERT)
            action = 'insert_update';
        }

        // 2. Optimistic UI: Actualizar estado de React INMEDIATAMENTE de forma segura
        setFeedbacks(prev => {
            const up = { ...prev };
            if (action === 'delete') {
                delete up[urlHash];
            } else {
                up[urlHash] = type;
            }
            return up;
        });

        // 3. Petición a base de datos en segundo plano mediante la capa de servicios
        try {
            if (action === 'delete') {
                await removeFeedback(user.id, urlHash);
            } else {
                await saveFeedback(user.id, urlHash, type);
            }
        } catch (err) {
            console.error("Error guardando feedback:", err);
            // Si falla la BD, revertimos usando functional update
            setFeedbacks(prev => {
                const up = { ...prev };
                if (currentType === undefined) {
                    delete up[urlHash];
                } else {
                    up[urlHash] = currentType;
                }
                return up;
            });
        }
    }, [user, feedbacks]);

    return { feedbacks, toggleFeedback, loading };
}

export default useFeedback;
