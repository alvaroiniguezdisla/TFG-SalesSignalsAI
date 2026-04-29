export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Llama al Backend para descargarse la lista de noticias (devuelve un array JSON)
export async function getNoticias() {
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
}

// Llama al Backend para descargarse las categorías oficiales de los filtros
export async function getCategories() {
    try {
        const response = await fetch(`${API_URL}/noticias/categorias`);
        if (!response.ok) throw new Error("Error al cargar categorías");
        return await response.json();
    } catch (error) {
        console.error("Error obteniendo categorías:", error);
        return { signals: [], products: [] }; // Fallback seguro
    }
}

export async function refreshNews() {
    try {
        const response = await fetch(`${API_URL}/refrescar`, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        return await response.json();

    } catch (error) {
        console.error("Error refrescando noticias:", error);
        throw error;
    }

}

export async function getNoticiaById(id) {
    try {
        const response = await fetch(`${API_URL}/noticias/${id}`);
        if (!response.ok) throw new Error("Noticia no encontrada");
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
}
