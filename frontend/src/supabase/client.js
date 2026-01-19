import { createClient } from '@supabase/supabase-js';

const projectUrl= import.meta.env.VITE_SUPABASE_URL;
const projectKey= import.meta.env.VITE_SUPABASE_ANON_KEY;

//Creamos conexion y la exportamos para usarla en toda la aplicacion
export const supabase = createClient(projectUrl, projectKey);

