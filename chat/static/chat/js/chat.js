// -----------------------------------
//  Funcions principals del xat
// -----------------------------------

let chatMessages;
let chatErrors;

document.addEventListener('DOMContentLoaded', function () {

    // Inicializar variables globales
    chatMessages = document.getElementById('chat-messages');
    chatErrors = document.getElementById('chat-errors');
    const chatForm = document.getElementById('chat-form');

    if (!chatMessages) return;

    // Carregar missatges inicials
    loadMessages();

    // Polling: cada 3 segons
    setInterval(loadMessages, 3000);

    // Enviar missatge
    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            sendMessage();
        });
    }

    // Delegació d'esdeveniments per eliminar o destacar missatges
    chatMessages.addEventListener('click', function (e) {

        // Eliminar missatge
        if (e.target.classList.contains('delete-message')) {
            const messageId = e.target.dataset.messageId;
            if (confirm('Vols eliminar aquest missatge?')) {
                deleteMessage(messageId);
            }
        }

        // Destacar missatge
        if (e.target.classList.contains('highlight-message')) {
            const messageId = e.target.dataset.messageId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            fetch(`/chat/message/${messageId}/highlight/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) loadMessages();
                else alert('No tens permisos per destacar aquest missatge');
            })
            .catch(err => console.error('Error destacant missatge:', err));
        }
    });

});

// -----------------------------------
//  Funció per carregar missatges
// -----------------------------------
function loadMessages() {
    if (typeof eventId === 'undefined') {
        console.error('eventId no està definit');
        return;
    }

    fetch(`/chat/${eventId}/messages/`)
        .then(response => {
            if (!response.ok) throw new Error('No s’ha pogut carregar el xat');
            return response.json();
        })
        .then(data => {
            const messages = data.messages;
            if (!chatMessages) return;
            chatMessages.innerHTML = '';

            messages.forEach(msg => {
                const msgEl = createMessageElement(msg);
                chatMessages.appendChild(msgEl);
            });

            scrollToBottom();
            updateMessageCount(messages.length);
        })
        .catch(err => console.error('Error carregant missatges:', err));
}

// -----------------------------------
//  Funció per enviar missatge
// -----------------------------------
function sendMessage() {
    const textarea = document.querySelector('#chat-form textarea');
    if (!textarea) return;

    const message = textarea.value.trim();
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    // Validación en frontend
    if (!message) {
        if (chatErrors) chatErrors.textContent = 'El missatge no pot estar buit';
        return;
    }

    if (message.length > 500) {
        if (chatErrors) chatErrors.textContent = 'Màxim 500 caràcters';
        return;
    }

    fetch(`/chat/${eventId}/send/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `message=${encodeURIComponent(message)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            textarea.value = '';
            if (chatErrors) chatErrors.textContent = '';
            loadMessages();
        } else {
            if (chatErrors) chatErrors.textContent = data.errors?.message || data.error || 'Error en enviar el missatge';
        }
    })
    .catch(err => {
        console.error('Error enviant missatge:', err);
        if (chatErrors) chatErrors.textContent = 'Error de connexió';
    });
}


// -----------------------------------
//  Funció per eliminar missatge
// -----------------------------------
function deleteMessage(messageId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) return;

    fetch(`/chat/message/${messageId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadMessages();
        } else {
            alert('No tens permisos per eliminar aquest missatge');
        }
    })
    .catch(err => console.error('Error eliminant missatge:', err));
}

// -----------------------------------
//  Funció per crear l'HTML d'un missatge
// -----------------------------------
function createMessageElement(msg) {
    const div = document.createElement('div');
    div.classList.add('chat-message');
    if (msg.is_highlighted) div.classList.add('highlighted');
    div.dataset.messageId = msg.id;

    div.innerHTML = `
        <div class="message-header d-flex justify-content-between">
            <strong>${escapeHtml(msg.display_name)}</strong>
            <small class="text-muted">${escapeHtml(msg.created_at)}</small>
        </div>
        <div class="message-content">${escapeHtml(msg.message)}</div>
        <div class="message-actions text-end">
            ${msg.can_delete ? `<button class="btn btn-sm btn-outline-danger delete-message" data-message-id="${msg.id}">Eliminar</button>` : ''}
            ${msg.can_highlight ? `<button class="btn btn-sm btn-outline-warning highlight-message" data-message-id="${msg.id}">Destacar</button>` : ''}
        </div>
    `;
    return div;
}

// -----------------------------------
//  Fer scroll automàtic al final del xat
// -----------------------------------
function scrollToBottom() {
    if (!chatMessages) return;
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// -----------------------------------
//  Actualitzar comptador de missatges
// -----------------------------------
function updateMessageCount(count) {
    const badge = document.getElementById('message-count');
    if (badge) badge.textContent = count;
}

// -----------------------------------
//  Escapar HTML per evitar XSS
// -----------------------------------
function escapeHtml(text) {
    if (text == null) text = '';
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
