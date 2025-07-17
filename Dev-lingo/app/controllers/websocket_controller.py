from geventwebsocket import WebSocketError
from bottle import request
import json
from app.models.user_model import UserModel

# Dicionários para rastrear clientes e suas informações
client_info = {}
connected_clients = set()

def handle_ws(ws, secret):
    
    # Lida com conexões WebSocket, mensagens e desconexões. Recebe o segredo da sessão como um parâmetro para evitar erros de escopo.
    
    # Use o 'secret' passado como argumento para obter o cookie de forma segura
    import bottle
    session_data = bottle.request.get_cookie("session", secret=secret)
    
    email = session_data.get("email") if session_data else "Desconhecido"

    # --- Verificação na Conexão ---
    user_model = UserModel()
    user = user_model.get_user_by_email(email)
    role = user.get("role", "user") if user else "user"

    print(f"[WebSocket] Cliente conectado: {email} (Role: {role})")
    connected_clients.add(ws)
    client_info[ws] = {"email": email, "role": role}
    
    enviar_lista_usuarios()

    try:
        while True:
            msg = ws.receive()
            if msg is None:
                break
            
            # Espera-se que todas as mensagens sejam no formato JSON
            try:
                data = json.loads(msg)
                if data.get("tipo") == "force_disconnect":
                    handle_force_disconnect(ws, data)

            except json.JSONDecodeError:
                print(f"[WebSocket] Mensagem não-JSON recebida de {email}: {msg}")
            except Exception as e:
                print(f"[WebSocket] Erro ao processar mensagem de {email}: {e}")

    except WebSocketError as e:
        print(f"[WebSocket] Erro de WebSocket para {email}: {e}")
    finally:
        # --- Limpeza na Desconexão ---
        if ws in connected_clients:
            connected_clients.remove(ws)
            client_info.pop(ws, None)
            print(f"[WebSocket] Cliente desconectado: {email}")
            enviar_lista_usuarios()

def handle_force_disconnect(sender_ws, data):
    
    # Lida com uma solicitação de um administrador para desconectar outro usuário.
    
    sender_info = client_info.get(sender_ws)
    
    # SEGURANÇA: Verifica se o remetente é um administrador
    if not sender_info or sender_info.get("role") != "admin":
        print(f"[WebSocket] Permissão negada para {sender_info.get('email')} tentar deslogar um usuário.")
        return

    target_email = data.get("email")
    if not target_email:
        return

    print(f"[WebSocket] Admin '{sender_info.get('email')}' requisitou desconexão de '{target_email}'.")

    # Encontra o cliente alvo para desconectar
    target_ws = None
    for ws, info in client_info.items():
        if info.get("email") == target_email:
            # Impede que um administrador seja desconectado por este método
            if info.get("role") == "admin":
                print(f"[WebSocket] Tentativa de desconectar um administrador ({target_email}) foi bloqueada.")
                return
            target_ws = ws
            break
            
    if target_ws:
        try:
            # Envia um motivo antes de fechar - bom para o feedback no lado do cliente
            payload = json.dumps({"tipo": "aviso_desconexao", "motivo": "Sua sessão foi encerrada por um administrador."})
            target_ws.send(payload)
            target_ws.close()
            print(f"[WebSocket] Conexão para {target_email} foi fechada.")
        except WebSocketError as e:
            print(f"[WebSocket] Erro ao tentar fechar a conexão de {target_email}: {e}")
    else:
        print(f"[WebSocket] Não foi possível encontrar o usuário online: {target_email}")


def enviar_lista_usuarios():
    
    # Envia a lista atualizada de usuários online para todos os clientes conectados.
    
    usuarios_online = [info["email"] for info in client_info.values()]
    roles_map = {info["email"]: info["role"] for info in client_info.values()}
    
    payload = {
        "tipo": "usuarios_online",
        "usuarios": usuarios_online,
        "roles": roles_map
    }
    mensagem = json.dumps(payload)
    
    # Itera sobre uma cópia do conjunto para modificação segura durante a iteração
    for client in list(connected_clients):
        try:
            client.send(mensagem)
        except Exception:
            # O cliente pode ter se desconectado abruptamente
            pass
