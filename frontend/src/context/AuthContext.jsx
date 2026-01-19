import { createContext, useContext, useEffect, useState } from "react";
import { supabase } from '../supabase/client';

//Creamos un "espacio" donde  guardaremos los datos del usuario
const AuthContext= createContext();

export const AuthProvider = ({ children}) => {
    const [user, setUser] = useState(null);//Datos técnicos(email,id)
    const [profile,setProfile]= useState(null);//Datos humanos(nombre,empresa)
    const [loading,setLoading]= useState(true);//Para saber si está cargando

    useEffect(() => {
        //Nada mas entrar preguntamos si hay alguien conectado
        const getSession= async ()=>{
            const {data:{session}} = await supabase.auth.getSession();
            setUser(session?.user ?? null);
            if (session?.user)await fetchProfile(session.user.id);  
            setLoading(false);
        }
        getSession();

        //Nos quedamos escuchando cambios(Login, Logout, Registro)
        const {data: {subscription}} = supabase.auth.onAuthStateChange(async(_event,session)=>{
            setUser(session?.user ?? null);
            if (session?.user){
                await fetchProfile(session.user.id);
            }else{
                setProfile(null);
            }
            setLoading(false);

        });

        //Cerrar suscripcion al salir
        return () => subscription.unsubscribe();
        
    }, [])

    //Funcion auxiliar para cargar el perfil de la tabla 'profiles'
    const fetchProfile = async (userId) => {
        try{
            const {data,error} = await supabase
            .from('profiles')
            .select('*')
            .eq('id',userId)
            .single();

        if (error) throw error;
        setProfile(data);
        }catch(error){
            console.error('Error al cargar el perfil:',error);
            setProfile(null);
        }
    };

    //Funcion para iniciar sesion
    const signIn = async (email,password) => {
        const {error} = await supabase.auth.signInWithPassword({email,password});
        if (error) throw error;
    };

    //Funcion para cerrar sesion
    const signOut = async () => {
        const {error} = await supabase.auth.signOut();
        if (error) throw error;
    };

    //Funcion para registrarse
    const signUp = async (email,password, userData) => {
        const {error} = await supabase.auth.signUp({
            email,
            password,
            options:{
                data:userData//lo que pone el usuario en el registro
            }
        });
        if (error) throw error;
    };

    //Funcion para actualizar perfil
    const updateProfile = async (profileData) => {
        const {error} = await supabase.from('profiles').update(profileData).eq('id',user.id);
        if (error) throw error;
        await fetchProfile(user.id);
    };
    
    //Exportamos todo para que la app lo use
    return (
        <AuthContext.Provider value={{user,profile,loading,signIn,signOut,signUp,updateProfile}}>
            {children}
        </AuthContext.Provider>
    );

    };

    //Hook para usar el contexto en cualquier pagina
    export const useAuth = () => {
        return useContext(AuthContext);
    };