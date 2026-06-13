"""
Módulo de Autenticação
======================
Sistema de autenticação com proteção contra força bruta e controle de sessão.

Funcionalidades:
- Login/logout de usuários
- Verificação de senha com bcrypt
- Proteção contra ataques de força bruta
- Controle de timeout de sessão
- Bloqueio temporário após múltiplas tentativas
"""

import streamlit as st
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    import bcrypt
except ModuleNotFoundError:
    bcrypt = None

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False

# Carregar variáveis de ambiente a partir da raiz do projeto
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# =========================
# Configurações de Segurança
# =========================

def get_env_str(name: str, default: str = "") -> str:
    """
    Lê uma variável do ambiente removendo espaços excedentes.
    """
    return (os.getenv(name, default) or "").strip()


SESSION_TIMEOUT_MINUTES = int(get_env_str("SESSION_TIMEOUT_MINUTES", "60"))
"""Tempo em minutos até a sessão expirar por inatividade"""

MAX_LOGIN_ATTEMPTS = int(get_env_str("MAX_LOGIN_ATTEMPTS", "10"))
"""Número máximo de tentativas de login antes de bloquear"""

LOGIN_LOCKOUT_MINUTES = int(get_env_str("LOGIN_LOCKOUT_MINUTES", "60"))
"""Tempo em minutos que a conta fica bloqueada após exceder tentativas"""

AUTH_ENABLED = get_env_str("AUTH_ENABLED", "false").lower() in {"1", "true", "yes", "sim"}
"""Ativa/desativa a tela de login. Por padrão o app fica aberto."""


def is_auth_enabled() -> bool:
    """
    Retorna True quando a autenticação por usuário/senha está ativa.
    """
    return AUTH_ENABLED

# =========================
# Usuários (carregados do .env)
# =========================

def get_users() -> dict[str, str]:
    """
    Retorna os usuários e hashes atualizados a partir do .env.

    Recarrega o arquivo para refletir alterações feitas sem reiniciar o app.
    """
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    return {
        "mjandussi": get_env_str("USER_MJANDUSSI", ""),
        "belem": get_env_str("USER_BELEM", ""),
        "subcont": get_env_str("USER_SUBCONT", ""),
    }


def normalize_username(username: str) -> str:
    """
    Normaliza o nome do usuário para comparação interna.
    """
    return (username or "").strip().lower()


# =========================
# Funções de Verificação
# =========================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash bcrypt.

    Args:
        plain_password (str): Senha em texto plano
        hashed_password (str): Hash bcrypt da senha

    Returns:
        bool: True se a senha corresponde, False caso contrário

    Examples:
        >>> hashed = "$2b$12$..."
        >>> verify_password("senha123", hashed)
        True
    """
    if not hashed_password:
        return False

    if bcrypt is None:
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def is_account_locked(username: str) -> bool:
    """
    Verifica se a conta está bloqueada por excesso de tentativas.

    Args:
        username (str): Nome do usuário

    Returns:
        bool: True se a conta está bloqueada, False caso contrário
    """
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = {}

    if username in st.session_state["login_attempts"]:
        attempts_data = st.session_state["login_attempts"][username]

        if attempts_data["count"] >= MAX_LOGIN_ATTEMPTS:
            lockout_time = attempts_data["last_attempt"] + timedelta(
                minutes=LOGIN_LOCKOUT_MINUTES
            )

            if datetime.now() < lockout_time:
                return True
            else:
                # Reset após expiração do bloqueio
                st.session_state["login_attempts"][username] = {
                    "count": 0,
                    "last_attempt": None
                }

    return False


def record_login_attempt(username: str, success: bool):
    """
    Registra tentativa de login (sucesso ou falha).

    Args:
        username (str): Nome do usuário
        success (bool): True se login bem-sucedido, False se falhou

    Side Effects:
        Atualiza st.session_state["login_attempts"]
    """
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = {}

    if success:
        # Limpar tentativas em caso de sucesso
        if username in st.session_state["login_attempts"]:
            del st.session_state["login_attempts"][username]
    else:
        # Incrementar contador de falhas
        if username not in st.session_state["login_attempts"]:
            st.session_state["login_attempts"][username] = {
                "count": 0,
                "last_attempt": None
            }

        st.session_state["login_attempts"][username]["count"] += 1
        st.session_state["login_attempts"][username]["last_attempt"] = datetime.now()


def check_session_timeout() -> bool:
    """
    Verifica se a sessão expirou por inatividade.

    Returns:
        bool: True se sessão válida, False se expirou

    Side Effects:
        - Atualiza timestamp de última atividade
        - Faz logout se sessão expirou
    """
    if "last_activity" in st.session_state:
        timeout = timedelta(minutes=SESSION_TIMEOUT_MINUTES)

        if datetime.now() - st.session_state["last_activity"] > timeout:
            logout()
            return False

    # Atualizar timestamp de última atividade
    st.session_state["last_activity"] = datetime.now()
    return True


# =========================
# Funções Principais
# =========================

def is_authed() -> bool:
    """
    Verifica se o usuário está autenticado e a sessão está válida.

    Returns:
        bool: True se autenticado e sessão válida, False caso contrário

    Examples:
        >>> if is_authed():
        ...     # Usuário pode acessar a página
        ...     show_content()
        ... else:
        ...     st.switch_page("app.py")
    """
    if not is_auth_enabled():
        return True

    if st.session_state.get("user") is None:
        return False

    return check_session_timeout()


def set_authed(user: str):
    """
    Define o usuário como autenticado e inicializa a sessão.

    Args:
        user (str): Nome do usuário autenticado

    Side Effects:
        - Define st.session_state["user"]
        - Inicializa timestamp de última atividade
    """
    st.session_state["user"] = user
    st.session_state["last_activity"] = datetime.now()


def logout():
    """
    Realiza logout e limpa toda a sessão do usuário.

    Side Effects:
        Limpa completamente st.session_state
    """
    st.session_state.clear()


def authenticate(username: str, password: str) -> tuple[bool, str]:
    """
    Autentica usuário com proteção contra ataques de força bruta.

    Implementa:
    - Verificação de conta bloqueada
    - Validação de credenciais com bcrypt
    - Registro de tentativas (sucesso/falha)
    - Mensagens informativas ao usuário

    Args:
        username (str): Nome do usuário
        password (str): Senha em texto plano

    Returns:
        tuple[bool, str]: (sucesso, mensagem)
            - sucesso: True se autenticado, False caso contrário
            - mensagem: Mensagem descritiva do resultado

    Examples:
        >>> success, message = authenticate("user", "senha123")
        >>> if success:
        ...     st.success(message)
        ...     st.switch_page("pages/0_Home.py")
        ... else:
        ...     st.error(message)
    """
    if not is_auth_enabled():
        set_authed("publico")
        return True, "Acesso liberado."

    if bcrypt is None:
        return False, "⚠️ Instale o pacote bcrypt para usar autenticação."

    username = normalize_username(username)

    if not username or not password:
        return False, "❌ Informe usuário e senha."

    # Verificar se a conta está bloqueada
    if is_account_locked(username):
        remaining_time = LOGIN_LOCKOUT_MINUTES

        if username in st.session_state.get("login_attempts", {}):
            lockout_end = (
                st.session_state["login_attempts"][username]["last_attempt"]
                + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
            )
            remaining_time = int((lockout_end - datetime.now()).total_seconds() / 60) + 1

        return False, f"⚠️ Conta bloqueada. Tente novamente em {remaining_time} minuto(s)."

    users = get_users()

    # Verificar credenciais
    if username in users:
        hashed_password = users[username]

        if verify_password(password, hashed_password):
            record_login_attempt(username, success=True)
            set_authed(username)
            return True, f"✅ Login realizado com sucesso! Bem-vindo(a), {username}!"

        if not hashed_password:
            return False, f"⚠️ O usuário '{username}' não possui hash configurado no arquivo .env."

    # Falha na autenticação
    record_login_attempt(username, success=False)

    # Calcular tentativas restantes
    attempts_count = (
        st.session_state.get("login_attempts", {})
        .get(username, {})
        .get("count", 0)
    )
    remaining_attempts = MAX_LOGIN_ATTEMPTS - attempts_count

    if remaining_attempts > 0:
        return False, (
            f"❌ Usuário ou senha inválidos. "
            f"{remaining_attempts} tentativa(s) restante(s)."
        )
    else:
        return False, (
            f"🔒 Conta bloqueada por {LOGIN_LOCKOUT_MINUTES} minutos "
            f"devido a múltiplas tentativas."
        )


# =========================
# Informações da Sessão
# =========================

def get_current_user() -> str | None:
    """
    Retorna o usuário atualmente autenticado.

    Returns:
        str | None: Nome do usuário ou None se não autenticado
    """
    if not is_auth_enabled():
        return None

    return st.session_state.get("user")


def restricted_ranking_fixed_ente() -> tuple[str, str] | None:
    """
    Se o perfil atual fixa ente na página de validações do ranking,
    retorna (tipo_ente, código) com tipo_ente 'E' ou 'M':
    - 'M': código é ID_ENTE (SICONFI), como na base de municípios;
    - 'E': código é COD_IBGE do estado (ex.: 33 = Rio de Janeiro).
    Caso contrário None.
    """
    if not is_auth_enabled():
        return None

    u = normalize_username(get_current_user() or "")
    if u == "belem":
        return ("M", "1501402")
    if u == "subcont":
        return ("E", "33")
    return None


def restricted_ranking_fixed_municipio_id() -> str | None:
    """
    Compatibilidade: se o perfil fixa apenas município, retorna o ID_ENTE; senão None.
    Perfis que fixam estado (ex.: subcont) não usam este retorno — use restricted_ranking_fixed_ente.
    """
    spec = restricted_ranking_fixed_ente()
    if spec and spec[0] == "M":
        return spec[1]
    return None


def get_session_info() -> dict:
    """
    Retorna informações sobre a sessão atual.

    Returns:
        dict: Dicionário com informações da sessão:
            - user: nome do usuário
            - last_activity: timestamp da última atividade
            - timeout_minutes: minutos até timeout
    """
    return {
        "user": st.session_state.get("user"),
        "last_activity": st.session_state.get("last_activity"),
        "timeout_minutes": SESSION_TIMEOUT_MINUTES,
    }


def require_login(app_name: str = "CRUZAMENTOS SICONFI") -> None:
    """
    Garante que a página só seja acessível por usuário autenticado.

    Se não autenticado (ou sessão expirada), redireciona para a página de login.
    """
    _ = app_name
    if not is_auth_enabled():
        return

    if not is_authed():
        st.warning("Faça login para acessar esta página.")
        st.switch_page("app.py")
        st.stop()


def render_logout(label: str = "⎋ Sair", target: str = "app.py") -> None:
    """
    Renderiza botão de logout no local onde for chamado.
    """
    if st.button(label, key=f"logout_btn_{target}"):
        logout()
        st.switch_page(target)
