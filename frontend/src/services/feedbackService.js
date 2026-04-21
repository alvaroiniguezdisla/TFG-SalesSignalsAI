import { supabase } from '../supabase/client';

/**
 * Servicio para gestionar la comunicación con Supabase respecto al Feedback de Noticias.
 * Aisla la lógica de base de datos de los Hooks de React.
 */

// 1. Obtener todos los feedbacks del usuario
export async function getUserFeedbacks(userId) {
    if (!userId) return [];

    try {
        const { data, error } = await supabase
            .from('news_feedback')
            .select('noticia_url_hash, feedback')
            .eq('user_id', userId);

        if (error) throw error;
        return data || [];
    } catch (error) {
        console.error("Error en feedbackService.getUserFeedbacks:", error);
        throw error;
    }
}

// 2. Guardar o actualizar un feedback (Upsert)
export async function saveFeedback(userId, urlHash, type) {
    try {
        const { error } = await supabase
            .from('news_feedback')
            .upsert({
                user_id: userId,
                noticia_url_hash: urlHash,
                feedback: type
            }, {
                onConflict: 'user_id, noticia_url_hash'
            });

        if (error) {
            console.error("Error en feedbackService.saveFeedback:", error);
            throw error;
        }
        return true;
    } catch (error) {
        console.error("Error en feedbackService.saveFeedback:", error);
        throw error;
    }
}

// 3. Eliminar un feedback (Toggle off)
export async function removeFeedback(userId, urlHash) {
    try {
        const { error } = await supabase
            .from('news_feedback')
            .delete()
            .match({
                user_id: userId,
                noticia_url_hash: urlHash
            });

        if (error) throw error;
        return true;
    } catch (error) {
        console.error("Error en feedbackService.removeFeedback:", error);
        throw error;
    }
}
