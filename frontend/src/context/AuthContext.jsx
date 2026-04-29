import { createContext, useContext, useEffect, useState } from "react";
import { supabase } from '../supabase/client';

/**
 * CONTEXTO DE AUTENTICACIÓN 
 * 
 * Este componente actúa como el gestor de sesiones en tiempo real de la SPA (Single Page Application).
 * Al envolver la aplicación completa con <AuthProvider> desde main.jsx, garantizamos que 
 * CUALQUIER página o ruta del frontend pueda comprobar instantáneamente:
 * 
 * 1. ¿Hay una sesión de Supabase Auth activa? (Variable 'user')
 * 2. ¿Quién es la persona conectada? (Variable 'profile' con nombre, empresa, rol...)
 * 
 * Es la pieza clave de seguridad: si no hay usuario logueado, este contexto informará
 * al AppRouter para que bloquee el acceso a rutas privadas y redirija a /login.
 */
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);//Datos técnicos(email,id)
    const [profile, setProfile] = useState(null);//Datos humanos(nombre,empresa)
    const [loading, setLoading] = useState(true);//Para saber si está cargando
    const [profileResolved, setProfileResolved] = useState(false);//Para no bloquear toda la app al leer profiles

    const handleSession = (session) => {
        setUser(session?.user ?? null);
        if (session?.user) {
            setProfileResolved(false);
            fetchProfile(session.user.id).finally(() => setProfileResolved(true));
        } else {
            setProfile(null);
            setProfileResolved(true);
        }
    };

    useEffect(() => {
        // Nada mas entrar preguntamos si hay alguien conectado
        const getSession = async () => {
            try {
                const { data: { session }, error } = await supabase.auth.getSession();
                if (error) throw error;
                handleSession(session);
            } catch (error) {
                console.error('Error inicializando auth:', error);
                setProfile(null);
                setProfileResolved(true);
            } finally {
                setLoading(false);
            }
        };

        getSession();

        // Escuchar cambios (Login, Logout, etc.)
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            handleSession(session);
            setLoading(false);
        });

        return () => subscription.unsubscribe();
    }, []);

    // Obtiene el perfil del usuario desde Supabase
    const fetchProfile = async (userId) => {
        try {
            const { data, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', userId)
                .single();

            if (error) {
                // Si no existe perfil, no bloqueamos
                setProfile(null);
                return;
            }
            setProfile(data);
        } catch (error) {
            console.error('Error fetchProfile:', error);
            setProfile(null);
        }
    };

    //Funcion para iniciar sesion
    const signIn = async (email, password) => {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
    };

    //Funcion para cerrar sesion
    const signOut = async () => {
        const { error } = await supabase.auth.signOut();
        if (error) throw error;
    };

    //Funcion para registrarse
    const signUp = async (email, password, userData) => {
        const { error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: userData//lo que pone el usuario en el registro
            }
        });
        if (error) throw error;
    };

    //Funcion para actualizar perfil
    const updateProfile = async (profileData) => {
        const { error } = await supabase.from('profiles').update(profileData).eq('id', user.id);
        if (error) throw error;
        await fetchProfile(user.id);
    };

    //Funcion para recuperar contrasena
    const resetPassword = async (email) => {
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: `${window.location.origin}/actualizar-contrasena`,
        });
        if (error) throw error;
    };

    //Funcion para actualizar contrasena
    const updatePassword = async (newPassword) => {
        const { error } = await supabase.auth.updateUser({
            password: newPassword
        });
        if (error) throw error;
    };

    //Exportamos todo para que la app lo use
    return (
        <AuthContext.Provider value={{ user, profile, loading, profileResolved, signIn, signOut, signUp, updateProfile, resetPassword, updatePassword }}>
            {children}
        </AuthContext.Provider>
    );

};

//Hook para usar el contexto en cualquier pagina
export const useAuth = () => {
    return useContext(AuthContext);
};
