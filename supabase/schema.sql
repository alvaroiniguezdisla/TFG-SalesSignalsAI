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

-- Insertar la configuración inicial con valores de producción.
-- Si ya existe la fila, actualiza los valores para garantizar la configuración correcta.
INSERT INTO public.app_config (
  id,
  umbral_similitud,
  max_emails_ejecucion,
  delay_entre_emails,
  ollama_model,
  rss_sources,
  ai_prompt
)
VALUES (
  1,
  0.8,
  50,
  1,
  'llama3.1',
  '[
    {"url": "https://www.expansion.com/rss/empresas.xml",        "name": "Expansión",        "type": "rss", "scraper_url": "https://www.expansion.com/empresas.html"},
    {"url": "https://rss.elconfidencial.com/empresas/",          "name": "El Confidencial",  "type": "rss", "scraper_url": "https://www.elconfidencial.com/empresas/"},
    {"url": "https://cincodias.elpais.com/rss/cincodias/companias.xml", "name": "Cinco Días","type": "rss", "scraper_url": "https://cincodias.elpais.com/companias/"},
    {"url": "https://www.europapress.es/rss/rss.aspx?ch=136",    "name": "Europa Press",     "type": "rss", "scraper_url": "https://www.europapress.es/economia/"},
    {"url": "https://negocios.com/feed/?post_type=post&cat=25",  "name": "Negocios.com",     "type": "rss", "scraper_url": "https://negocios.com/category/negocios/empresas/"}
  ]'::jsonb,
  $prompt$ACTUA COMO: Un analista senior de ventas B2B de HP (Hewlett-Packard) con 15 años de experiencia.
TU OBJETIVO: Analizar una noticia y generar inteligencia comercial accionable para el equipo de ventas de HP.

PASO 2: ASIGNAR PRODUCTO HP
Elige la linea de producto MAS adecuada:
- "Gaming / OMEN": eSports, videojuegos, diseño gráfico.
- "Impresión y Escáner": Oficinas fisicas, gestion documental, logistica.
- "PC Consumo (Hogar/Estudiantes)": Usuarios finales, educación.
- "Soluciones Empresariales (ProBook/Elite)": Portatiles y PCs corporativos para empleados.
- "Servicios y Soluciones IT": Ciberseguridad, nube, gestion de flotas IT.
- "Otros / No Aplica": Si es ruido o no encaja.

PASO 3: IDENTIFICAR EMPRESAS Y CLASIFICAR SU TAMANO
Detecta las empresas mencionadas en la noticia (maximo 3). Para cada una, clasifica su tamano:
- "Startup": Menos de 50 empleados, rondas de financiacion, recien creada.
- "PYME": Entre 50 y 250 empleados, ambito local o regional.
- "Mediana Empresa": Entre 250 y 1000 empleados, presencia nacional.
- "Gran Cuenta": Mas de 1000 empleados, multinacionales, cotizadas en bolsa.
- "Desconocido": Si no hay datos suficientes.

PASO 4: RESUMEN COMERCIAL (resumen_comercial)
Escribe un resumen de 3-5 frases para el vendedor.

PASO 5: ARGUMENTARIO COMERCIAL (talk_track)
Genera exactamente 3-4 puntos que el comercial puede usar al llamar al cliente.

PASO 6: BORRADOR DE EMAIL (email_draft)
Escribe un email profesional de primer contacto (maximo 150 palabras).$prompt$
)
ON CONFLICT (id) DO UPDATE SET
  umbral_similitud      = EXCLUDED.umbral_similitud,
  max_emails_ejecucion  = EXCLUDED.max_emails_ejecucion,
  delay_entre_emails    = EXCLUDED.delay_entre_emails,
  ollama_model          = EXCLUDED.ollama_model,
  rss_sources           = EXCLUDED.rss_sources,
  ai_prompt             = EXCLUDED.ai_prompt,
  updated_at            = timezone('utc', now());


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
