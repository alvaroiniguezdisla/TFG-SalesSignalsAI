-- =============================================================================
-- SalesSignalsAI — Esquema de base de datos para Supabase
-- =============================================================================
-- Instrucciones:
--   1. Abre tu proyecto en https://supabase.com
--   2. Ve a SQL Editor (menú lateral izquierdo)
--   3. Pega todo este archivo y pulsa "Run"
--   4. Verifica en Table Editor que aparecen las 4 tablas
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. app_config
--    Tabla de configuración global del sistema (una sola fila con id = 1).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.app_config (
  id                    integer       NOT NULL CHECK (id = 1),
  umbral_similitud      numeric       DEFAULT 0.82,
  max_emails_ejecucion  integer       DEFAULT 50,
  delay_entre_emails    integer       DEFAULT 1,
  ollama_model          text          DEFAULT 'llama3.1',
  rss_sources           jsonb         NOT NULL DEFAULT '[]'::jsonb,
  updated_at            timestamptz   NOT NULL DEFAULT timezone('utc', now()),
  ai_prompt             text          DEFAULT '',
  CONSTRAINT app_config_pkey PRIMARY KEY (id)
);

-- Insertar la fila de configuración inicial si no existe
INSERT INTO public.app_config (id)
VALUES (1)
ON CONFLICT (id) DO NOTHING;


-- -----------------------------------------------------------------------------
-- 2. noticias
--    Almacena cada noticia procesada por el pipeline de IA.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.noticias (
  id                      uuid          NOT NULL DEFAULT gen_random_uuid(),
  url_hash                text          NOT NULL UNIQUE,
  url                     text          NOT NULL,
  titulo                  text          NOT NULL,
  resumen                 text,
  fuente                  text          NOT NULL,
  published_at            timestamptz   DEFAULT now(),
  scraped_at              timestamptz   DEFAULT now(),
  categoria_ia            text,
  relevancia_ia           integer       DEFAULT 0,
  resumen_comercial_ia    text,
  empresas_clave_ia       text[],
  urls_extra              jsonb         DEFAULT '[]'::jsonb,
  categoria_producto_ia   text          DEFAULT 'Otros / No Aplica',
  talk_track_ia           text          DEFAULT '',
  email_draft_ia          text          DEFAULT '',
  empresas_detalle_ia     jsonb         DEFAULT '[]'::jsonb,
  CONSTRAINT noticias_pkey PRIMARY KEY (id)
);


-- -----------------------------------------------------------------------------
-- 3. profiles
--    Perfil de cada usuario registrado. Se enlaza con auth.users de Supabase.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
  id                  uuid          NOT NULL,
  first_name          text,
  last_name           text,
  email               text,
  role                text          DEFAULT 'user',
  favorite_companies  text[]        DEFAULT '{}',
  favorite_categories text[]        DEFAULT '{}',
  created_at          timestamptz   NOT NULL DEFAULT timezone('utc', now()),
  updated_at          timestamptz   NOT NULL DEFAULT timezone('utc', now()),
  CONSTRAINT profiles_pkey PRIMARY KEY (id),
  CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
);


-- -----------------------------------------------------------------------------
-- 4. news_feedback
--    Valoraciones (like / dislike) que cada usuario hace sobre las noticias.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.news_feedback (
  id               uuid    NOT NULL DEFAULT gen_random_uuid(),
  user_id          uuid    NOT NULL,
  noticia_url_hash text    NOT NULL,
  feedback         text    NOT NULL CHECK (feedback IN ('like', 'dislike')),
  created_at       timestamptz NOT NULL DEFAULT timezone('utc', now()),
  CONSTRAINT news_feedback_pkey PRIMARY KEY (id),
  CONSTRAINT news_feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);


-- =============================================================================
-- TRIGGER: crear perfil automáticamente al registrar un nuevo usuario
-- =============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO public.profiles (id, email)
  VALUES (NEW.id, NEW.email)
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- Solo los usuarios autenticados pueden leer y modificar sus propios datos.
-- =============================================================================

-- profiles: cada usuario solo accede a su propia fila
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuarios ven su propio perfil"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Usuarios editan su propio perfil"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- news_feedback: cada usuario gestiona solo su propio feedback
ALTER TABLE public.news_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuarios ven su feedback"
  ON public.news_feedback FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Usuarios insertan su feedback"
  ON public.news_feedback FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuarios actualizan su feedback"
  ON public.news_feedback FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Usuarios eliminan su feedback"
  ON public.news_feedback FOR DELETE
  USING (auth.uid() = user_id);

-- noticias y app_config: lectura pública para usuarios autenticados
ALTER TABLE public.noticias ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Lectura pública de noticias"
  ON public.noticias FOR SELECT
  TO authenticated
  USING (true);

ALTER TABLE public.app_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Lectura pública de configuración"
  ON public.app_config FOR SELECT
  TO authenticated
  USING (true);
