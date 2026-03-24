"""
Servicio de envío de notificaciones mediante Microsoft Graph API (Delegated Flow).
Utiliza Device Code Flow para autenticar localmente y notificar a un chat 1:1 en Teams.
"""
import os
import logging
import requests
import msal
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class TeamsGraphService:
    def __init__(self):
        self.tenant_id = settings.GRAPH_TENANT_ID
        self.client_id = settings.GRAPH_CLIENT_ID
        self.scopes = settings.GRAPH_SCOPES.split() if settings.GRAPH_SCOPES else ["User.Read", "Chat.ReadBasic", "ChatMessage.Send"]
        self.target_email = settings.TEAMS_TARGET_USER_EMAIL
        
        # Archivo donde guardaremos la sesión (token) para no tener que hacer login cada vez
        self.cache_path = os.path.join(os.path.dirname(__file__), "msal_cache.bin")
        self.token_cache = msal.SerializableTokenCache()
        
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r") as f:
                self.token_cache.deserialize(f.read())
                
        self.app = msal.PublicClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            token_cache=self.token_cache
        )

    def _guardar_cache(self):
        """Si el token cambió, lo escribe en el caché local"""
        if self.token_cache.has_state_changed:
            with open(self.cache_path, "w") as f:
                f.write(self.token_cache.serialize())

    def get_token(self):
        """Obtiene un token de acceso: intenta silenciosamente, si no, levanta la interfaz de consola Device Flow"""
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
            if result and "access_token" in result:
                self._guardar_cache()
                return result["access_token"]
        
        # Si no hay token guardado o caducó, se lanza interactivo por consola
        logger.info("🔐 ¡ATENCIÓN! Revisa la consola: necesitas iniciar sesión en Microsoft para interactuar con Teams.")
        flow = self.app.initiate_device_flow(scopes=self.scopes)
        if "user_code" not in flow:
            raise ValueError(f"Fallo al crear inicialización Device FLow: {flow}")
            
        print("\n" + "!"*60)
        print(">>> INICIO DE SESIÓN EN MICROSOFT (NECESARIO PARA TEAMS) <<<")
        print(flow["message"])
        print("!"*60 + "\n")
        
        result = self.app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            self._guardar_cache()
            return result["access_token"]
        else:
            raise RuntimeError(f"Fallo de autenticación en Microsoft Graph: {result.get('error_description')}")

    def _crear_o_recuperar_espacio_propio(self, token: str) -> Optional[str]:
        """Recupera o crea un chat de grupo que sirve como buzón exclusivo y limpio para las notificaciones"""
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
        topic_name = "SalesSignals Alertas"
        
        try:
            # 1. Buscar si ya existe para no crear duplicados
            resp = requests.get("https://graph.microsoft.com/v1.0/me/chats", headers={'Authorization': 'Bearer ' + token})
            resp.raise_for_status()
            for chat in resp.json().get("value", []):
                if chat.get("topic") == topic_name:
                    return chat["id"]
            
            # 2. Obtener el ID GUID real del usuario (obligatorio para crear chats por API)
            me_resp = requests.get("https://graph.microsoft.com/v1.0/me", headers={'Authorization': 'Bearer ' + token})
            me_resp.raise_for_status()
            my_id = me_resp.json()["id"]
            
            # 3. Crear un chat de grupo donde el único miembro eres tú
            payload = {
                "chatType": "group",
                "topic": topic_name,
                "members": [
                    {
                        "@odata.type": "#microsoft.graph.aadUserConversationMember",
                        "roles": ["owner"],
                        "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{my_id}')"
                    }
                ]
            }
            create_resp = requests.post("https://graph.microsoft.com/v1.0/chats", headers=headers, json=payload)
            create_resp.raise_for_status()
            return create_resp.json()["id"]
                
        except Exception as e:
            logger.error(f"Error creando el buzón de SalesSignals en Graph: {e}")
            
        return None

    def enviar_notificacion(self, destinatario: str, nombre: str, noticias: list) -> bool:
        if not noticias:
            return False

        if not self.tenant_id or not self.client_id:
            logger.warning("Credenciales GRAPH_TENANT_ID o GRAPH_CLIENT_ID no configuradas en el entorno.")
            return False

        try:
            # 1. Autenticar
            token = self.get_token()
            
            # 2. Conseguir el ID de la sala de chat
            chat_id = self._crear_o_recuperar_espacio_propio(token)
            if not chat_id:
                logger.error("No se ha podido localizar un ChatID válido para mandar la notificación.")
                return False

            # 3. Construir HTML sencillo del mensaje
            lista_html = "".join([f"<li><b>{n.get('titulo')}</b> - <a href='{n.get('url', '#')}'>Enlace a la noticia</a></li>" for n in noticias[:5]])
            payload = {
                "body": {
                    "contentType": "html",
                    "content": f"<h3>[TFG] SalesSignals Alert</h3><p>Hola {nombre}, tienes <b>{len(noticias)} nuevas señales</b> identificadas por la Inteligencia Artificial.</p><ul>{lista_html}</ul><p><em>(Ve al dashboard local para gestionarlas).</em></p>"
                }
            }

            # 4. Enviar mediante Graph
            headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
            resp = requests.post(f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages", headers=headers, json=payload)
            resp.raise_for_status()
            
            logger.info("Notificación enviada instantáneamente al chat de Teams.")
            return True

        except Exception as e:
            logger.error(f"Error fatal enviando la notificación a Teams: {e}")
            return False

_teams_graph_service_instance = None

def get_teams_graph_service() -> TeamsGraphService:
    global _teams_graph_service_instance
    if _teams_graph_service_instance is None:
        _teams_graph_service_instance = TeamsGraphService()
    return _teams_graph_service_instance
