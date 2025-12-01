// Definimos la URL base de nuestro backend
// En un futuro esto podría venir de una variable de entorno (.env)
const API_URL = 'http://localhost:8000';

/**
 * Obtiene las últimas noticias del backend.
 * @returns {Promise<Array>} Lista de noticias
 */
export const getNoticias = async () => {
    try {
        const response = await fetch(`${API_URL}/noticias`);

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error en el servicio de noticias:", error);
        throw error;
    }
};
