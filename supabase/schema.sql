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

-- Insertar noticias demo para que el frontend tenga contenido tras crear la base de datos.
-- Si ya existen, se actualizan por url_hash para evitar duplicados al re-ejecutar el script.
INSERT INTO public.noticias (
  url_hash,
  url,
  titulo,
  resumen,
  fuente,
  published_at,
  scraped_at,
  categoria_ia,
  relevancia_ia,
  resumen_comercial_ia,
  empresas_clave_ia,
  urls_extra,
  categoria_producto_ia,
  talk_track_ia,
  email_draft_ia,
  empresas_detalle_ia
)
VALUES
(
  'db6ade9cdd2937a090b18708cdb34ca9',
  'https://www.europapress.es/economia/finanzas-00340/noticia-santander-gana-5455-millones-marzo-603-mas-gracias-plusvalia-polonia-20260429071148.html',
  'Santander gana 5.455 millones hasta marzo, un 60,3% más gracias a la plusvalía de Polonia',
  'El Banco Santander obtuvo un beneficio neto de 5.455 millones de euros en el primer trimestre de 2026, lo que supone un incremento del 60,3% en comparación con el mismo periodo de 2025.',
  'Europa Press',
  '2026-04-29 05:11:48+00',
  '2026-04-29 09:53:12+00',
  'Resultados Financieros',
  85,
  'Santander presenta un fuerte crecimiento de beneficios, lo que indica capacidad presupuestaria para nuevas inversiones tecnológicas. Es una oportunidad para plantear soluciones de puesto de trabajo corporativo, renovación de equipos y servicios de soporte para grandes cuentas.',
  ARRAY['Banco Santander'],
  '[]'::jsonb,
  'Soluciones Empresariales (ProBook/Elite)',
  '1. Santander está en un momento financiero favorable para abordar proyectos de eficiencia interna. 2. HP puede ayudar en renovación de parque corporativo y gestión del puesto de trabajo. 3. Una propuesta orientada a productividad y reducción de costes encaja con el contexto de resultados.',
  'Asunto: Oportunidad de eficiencia tecnológica para Santander\n\nHola [Nombre],\nHe visto los resultados recientes de Santander y el fuerte crecimiento del beneficio en el primer trimestre. Desde HP creemos que este puede ser un buen momento para revisar iniciativas de productividad, renovación de equipos corporativos y gestión del puesto de trabajo.\n\nMe gustaría comentar cómo podríamos apoyar a vuestro equipo con soluciones empresariales adaptadas a una gran cuenta financiera.\n\nUn saludo,\n[Tu nombre]',
  '[{"nombre": "Banco Santander", "tamano": "Gran Cuenta"}]'::jsonb
),
(
  '4df336d7e276727d2e22e589ef49d758',
  'https://www.europapress.es/economia/noticia-redeia-eleva-18-beneficio-marzo-140-millones-impulsa-inversiones-350-millones-20260429081251.html',
  'Redeia eleva un 1,8% su beneficio a marzo, hasta 140 millones, e impulsa inversiones hasta los 350 millones',
  'Redeia obtuvo un beneficio neto de 140,3 millones de euros en el primer trimestre e impulsó sus inversiones hasta los 350 millones.',
  'Europa Press',
  '2026-04-29 06:12:51+00',
  '2026-04-29 09:53:12+00',
  'Transformación Digital',
  75,
  'Redeia combina estabilidad financiera con un aumento relevante de inversión. Para HP, el ángulo comercial más claro está en servicios IT, gestión de flotas, seguridad y soporte tecnológico para una compañía crítica del sector energético.',
  ARRAY['Redeia'],
  '[]'::jsonb,
  'Servicios y Soluciones IT',
  '1. El aumento de inversión abre conversación sobre modernización tecnológica. 2. La criticidad del negocio exige continuidad, seguridad y gestión eficiente del parque IT. 3. HP puede posicionarse como socio para servicios gestionados y protección de endpoints.',
  'Asunto: Apoyo tecnológico para el plan inversor de Redeia\n\nHola [Nombre],\nHe leído que Redeia está impulsando sus inversiones en 2026. Desde HP podemos ayudar a convertir ese esfuerzo inversor en mejoras concretas de productividad, seguridad y gestión del parque tecnológico.\n\n¿Te parece si agendamos una breve llamada para revisar posibles áreas de apoyo?\n\nUn saludo,\n[Tu nombre]',
  '[{"nombre": "Redeia", "tamano": "Gran Cuenta"}]'::jsonb
),
(
  'ee6caa8bf3351e4438251233702dd126',
  'https://www.elconfidencial.com/empresas/2026-04-28/cotizacion-holaluz-subida-bolsa-negocio-venta-gas-natural_4346260/',
  'Holaluz despunta un 9,5% en bolsa tras volver al negocio de venta de gas natural',
  'Holaluz vuelve al negocio de venta de gas natural más de tres años después y el mercado reacciona con una subida del 9,5% en bolsa.',
  'El Confidencial',
  '2026-04-28 09:19:00+00',
  '2026-04-29 09:53:12+00',
  'Expansión / Crecimiento ',
  70,
  'Holaluz retoma una línea de negocio y entra en una fase de crecimiento operativo. La oportunidad comercial está en acompañar esa expansión con equipos corporativos, escalabilidad IT y servicios que reduzcan fricción en nuevos procesos internos.',
  ARRAY['Holaluz'],
  '[]'::jsonb,
  'Soluciones Empresariales (ProBook/Elite)',
  '1. La vuelta al negocio de gas puede requerir refuerzo operativo y nuevos equipos. 2. HP puede apoyar la escalabilidad con soluciones de puesto de trabajo y servicios IT. 3. El enfoque debe ser crecimiento ordenado, productividad y control de costes.',
  'Asunto: Tecnología para acompañar el crecimiento de Holaluz\n\nHola [Nombre],\nHe visto la noticia sobre la vuelta de Holaluz al negocio de venta de gas natural. En una fase de expansión, contar con una base tecnológica escalable puede ayudar a crecer sin perder eficiencia operativa.\n\nDesde HP podemos apoyar con soluciones corporativas y servicios IT adaptados a equipos en crecimiento.\n\nUn saludo,\n[Tu nombre]',
  '[{"nombre": "Holaluz", "tamano": "Gran Cuenta"}]'::jsonb
),
(
  '68c6f7b39b3c5b91714b1e2607fac668',
  'https://www.europapress.es/economia/finanzas-00340/noticia-mapfre-gana-311-millones-euros-primer-trimestre-127-mas-20260429074835.html',
  'Mapfre gana 311 millones de euros en el primer trimestre, un 12,7% más',
  'Mapfre obtuvo un beneficio neto de 310,9 millones de euros en el primer trimestre, un 12,7% más que en el mismo periodo de 2025.',
  'Europa Press',
  '2026-04-29 05:48:35+00',
  '2026-04-29 09:53:12+00',
  'Resultados Financieros',
  55,
  'Mapfre mejora rentabilidad y resultados, pero la noticia no apunta a una necesidad tecnológica inmediata. Es una señal comercial media para iniciar seguimiento y detectar posibles proyectos internos de eficiencia, digitalización o renovación de equipos.',
  ARRAY['Mapfre'],
  '[]'::jsonb,
  'Servicios y Soluciones IT',
  '1. La mejora de rentabilidad puede facilitar conversaciones de inversión selectiva. 2. En seguros, la eficiencia operativa y la seguridad del puesto de trabajo son temas relevantes. 3. Conviene abrir una conversación exploratoria sin asumir urgencia de compra.',
  'Asunto: Seguimiento de iniciativas tecnológicas en Mapfre\n\nHola [Nombre],\nHe visto los resultados positivos de Mapfre en el primer trimestre. Desde HP estamos trabajando con grandes organizaciones en eficiencia del puesto de trabajo, seguridad y servicios IT.\n\nMe gustaría conocer si tenéis alguna iniciativa tecnológica prevista para los próximos meses.\n\nUn saludo,\n[Tu nombre]',
  '[{"nombre": "Mapfre", "tamano": "Gran Cuenta"}]'::jsonb
),
(
  'cd216017e124a0dff353a48f4650913a',
  'https://www.europapress.es/economia/noticia-aena-gana-329-millones-marzo-93-mas-eleva-ingresos-116-20260429081436.html',
  'Aena gana 329 millones hasta marzo, un 9,3% más, y eleva sus ingresos un 11,6%',
  'Aena aumentó sus ingresos y centró parte de su inversión en la mejora de instalaciones y seguridad operacional de los aeropuertos.',
  'Europa Press',
  '2026-04-29 06:14:36+00',
  '2026-04-29 09:53:12+00',
  'Resultados Financieros',
  35,
  'Aena muestra buenos resultados e inversión en instalaciones, aunque la relación con HP es menos directa que en otras señales. Puede servir como oportunidad de baja prioridad para explorar necesidades de dispositivos, soporte y seguridad en entornos operativos.',
  ARRAY['Aena'],
  '[]'::jsonb,
  'Impresión y Escáner',
  '1. La inversión en instalaciones puede implicar necesidades de soporte documental y dispositivos en operaciones. 2. HP puede aportar impresión gestionada, endpoints y servicios para entornos distribuidos. 3. Es una señal de seguimiento, no una oportunidad urgente.',
  'Asunto: Posibles necesidades tecnológicas en operaciones aeroportuarias\n\nHola [Nombre],\nHe visto que Aena está aumentando inversión en instalaciones y seguridad operacional. Desde HP podemos apoyar entornos distribuidos con soluciones de impresión, dispositivos corporativos y servicios gestionados.\n\nSi tiene sentido, me gustaría comentar posibles áreas de colaboración.\n\nUn saludo,\n[Tu nombre]',
  '[{"nombre": "Aena", "tamano": "Gran Cuenta"}]'::jsonb
)
ON CONFLICT (url_hash) DO UPDATE SET
  url = EXCLUDED.url,
  titulo = EXCLUDED.titulo,
  resumen = EXCLUDED.resumen,
  fuente = EXCLUDED.fuente,
  published_at = EXCLUDED.published_at,
  scraped_at = EXCLUDED.scraped_at,
  categoria_ia = EXCLUDED.categoria_ia,
  relevancia_ia = EXCLUDED.relevancia_ia,
  resumen_comercial_ia = EXCLUDED.resumen_comercial_ia,
  empresas_clave_ia = EXCLUDED.empresas_clave_ia,
  urls_extra = EXCLUDED.urls_extra,
  categoria_producto_ia = EXCLUDED.categoria_producto_ia,
  talk_track_ia = EXCLUDED.talk_track_ia,
  email_draft_ia = EXCLUDED.email_draft_ia,
  empresas_detalle_ia = EXCLUDED.empresas_detalle_ia;


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
