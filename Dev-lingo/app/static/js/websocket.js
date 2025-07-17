if (typeof WS_ENABLED !== 'undefined' && WS_ENABLED) {
    const socket = new WebSocket("ws://localhost:8080/ws");

    socket.onopen = () => console.log("[WS] Conectado ao servidor.");

    socket.onclose = () => {
        console.log("[WS] Desconectado do servidor WebSocket.");
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            if (data.tipo === "usuarios_online") {
                // Chama a nova função para atualizar a tabela principal
                updateUserStatusesInTable(data.usuarios, data.roles);
            } else if (data.tipo === "aviso_desconexao") {
                // Mostra um alerta se o usuário for desconectado por um admin
                alert(data.motivo);
                window.location.href = '/logout';
            } else {
                // Lógica para outras mensagens genéricas do WebSocket
                if (typeof onWebSocketMessage === "function") {
                    onWebSocketMessage(event.data);
                } else {
                    console.log("[WS] Mensagem genérica recebida:", event.data);
                }
            }
        } catch (e) {
            console.error("[WS] Erro ao processar mensagem do servidor:", event.data, e);
        }
    };

    /**
     * Função global para enviar mensagens através do WebSocket.
     * @param {Object | string} msg - A mensagem a ser enviada.
     */
    window.enviarWebSocket = (msg) => {
        if (socket.readyState === WebSocket.OPEN) {
            const message = typeof msg === 'object' ? JSON.stringify(msg) : msg;
            socket.send(message);
        }
    };
}

/**
 * Envia uma solicitação ao servidor para desconectar um usuário pelo email.
 * @param {string} email - O email do usuário a ser desconectado.
 */
function deslogarUsuario(email) {
    if (!confirm(`Tem certeza que deseja deslogar o usuário ${email}?`)) {
        return;
    }
    console.log(`[WS] Solicitando desconexão para: ${email}`);
    const payload = {
        tipo: "force_disconnect",
        email: email
    };
    window.enviarWebSocket(payload);
}

/**
 * Atualiza os status e botões na tabela principal de usuários.
 * @param {string[]} onlineUserEmails - Array com os emails dos usuários online.
 * @param {Object} userRoles - Mapa de email para role (ex: {'user@a.com': 'admin'})
 */
function updateUserStatusesInTable(onlineUserEmails, userRoles) {
    // Busca todas as linhas da tabela que correspondem a um usuário
    const allRows = document.querySelectorAll('tr[data-user-email]');

    // 1. Primeiro, reseta todos os usuários para o estado "Offline"
    // Isso garante que usuários que se desconectaram sejam atualizados corretamente.
    allRows.forEach(row => {
        const statusCell = row.querySelector('.status-cell');
        statusCell.innerHTML = '<span class="status-badge status-offline">Offline</span>';

        // Remove o botão "Deslogar" que pode ter sido adicionado anteriormente
        const logoutButton = row.querySelector('.btn-logout');
        if (logoutButton) {
            logoutButton.remove();
        }
    });

    // 2. Em seguida, atualiza o status apenas dos usuários que estão na lista de online
    onlineUserEmails.forEach(email => {
        const userRow = document.querySelector(`tr[data-user-email="${email}"]`);
        if (!userRow) return; // Ignora se o usuário online não estiver na tabela visível

        // Atualiza a célula de status para "Online"
        const statusCell = userRow.querySelector('.status-cell');
        statusCell.innerHTML = '<span class="status-badge status-online">Online</span>';

        // Adiciona o botão "Deslogar" apenas para usuários com role 'user'
        const userRole = userRoles[email];
        if (userRole === 'user') {
            const actionsCell = userRow.querySelector('.actions-cell .actions');
            
            // Verifica se o botão já não existe para não duplicar
            if (actionsCell && !actionsCell.querySelector('.btn-logout')) {
                const logoutButton = document.createElement('button');
                logoutButton.textContent = 'Deslogar';
                // Adiciona classes para estilização e para fácil identificação futura
                logoutButton.className = 'btn btn-delete btn-small btn-logout';
                logoutButton.onclick = () => deslogarUsuario(email);
                actionsCell.appendChild(logoutButton);
            }
        }
    });
}