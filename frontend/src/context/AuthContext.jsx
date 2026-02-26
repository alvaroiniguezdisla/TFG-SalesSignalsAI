import { createContext, useContext, useEffect, useState } from "react";
import { supabase } from '../supabase/client';

//Creamos un "espacio" donde  guardaremos los datos del usuario
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);//Datos técnicos(email,id)
    const [profile, setProfile] = useState(null);//Datos humanos(nombre,empresa)
    const [loading, setLoading] = useState(true);//Para saber si está cargando

    useEffect(() => {
        // Nada mas entrar preguntamos si hay alguien conectado
        const getSession = async () => {
            try {
                const { data: { session }, error } = await supabase.auth.getSession();
                if (error) throw error;

                setUser(session?.user ?? null);
                if (session?.user) {
                    // Cargamos perfil en segundo plano (sin await) para no bloquear la UI
                    fetchProfile(session.user.id);
                }
            } catch (error) {
                console.error('Error inicializando auth:', error);
            } finally {
                setLoading(false);
            }
        };

        getSession();

        // Escuchar cambios (Login, Logout, etc.)
        const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
            setUser(session?.user ?? null);
            if (session?.user) {
                // Cargamos perfil en segundo plano (sin await)
                fetchProfile(session.user.id);
            } else {
                setProfile(null);
            }
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
        <AuthContext.Provider value={{ user, profile, loading, signIn, signOut, signUp, updateProfile, resetPassword, updatePassword }}>
            {children}
        </AuthContext.Provider>
    );

};

//Hook para usar el contexto en cualquier pagina
export const useAuth = () => {
    return useContext(AuthContext);
};