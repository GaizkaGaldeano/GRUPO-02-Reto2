document.addEventListener('DOMContentLoaded', () => {
    // 1. Gestión del Año
    const yearSpan = document.getElementById('year');
    if (yearSpan) yearSpan.textContent = new Date().getFullYear();

    // 2. Navegación Móvil
    const navToggle = document.getElementById('navToggle');
    const primaryNav = document.getElementById('primaryNav');

    if (navToggle && primaryNav) {
        navToggle.addEventListener('click', () => {
            const isVisible = primaryNav.getAttribute('data-visible') === 'true';
            primaryNav.setAttribute('data-visible', !isVisible);
            navToggle.setAttribute('aria-expanded', !isVisible);
        });
    }

    // 3. CHAT IA - Variables
    const chatLauncher = document.getElementById('ai-chat-button');
    const chatWidget = document.getElementById('ai-chat-window');
    const chatClose = document.getElementById('ai-chat-close');
    const chatInput = document.getElementById('ai-chat-input');
    const chatMic = document.getElementById('ai-chat-mic');
    const chatSend = document.getElementById('ai-chat-send');
    const chatBody = document.getElementById('ai-chat-messages');

    // Abrir/Cerrar chat
    if (chatLauncher && chatWidget) {
        chatLauncher.onclick = () => {
            chatWidget.style.display = 'flex';
            chatLauncher.style.display = 'none';
        };
    }
    if (chatClose && chatLauncher) {
        chatClose.onclick = () => {
            chatWidget.style.display = 'none';
            chatLauncher.style.display = 'flex';
        };
    }

    // FUNCIÓN ENVIAR MENSAJE
    async function sendMessage(textOverride = null) {
        // Si textOverride tiene valor (voz), lo usa; si no, lee el input
        const text = (textOverride !== null && typeof textOverride === 'string' 
                     ? textOverride 
                     : chatInput.value).trim();
        
        if (!text || !chatBody) return;
        
        // Mostrar mensaje del usuario
        const userDiv = document.createElement("div" );
        userDiv.className = "ai-message user";
        userDiv.textContent = text;
        chatBody.appendChild(userDiv);
        
        chatInput.value = ""; 
        chatBody.scrollTop = chatBody.scrollHeight;

        try {
            const response = await fetch("http://85.50.79.98:5005/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pregunta: text }) 
            });

            const data = await response.json();
            const botDiv = document.createElement("div");
            botDiv.className = "ai-message bot";
            botDiv.textContent = data.respuesta || "🤖 Lo siento, hubo un problema.";
            chatBody.appendChild(botDiv);

        } catch (e) { 
            const errorDiv = document.createElement("div");
            errorDiv.className = "ai-message bot";
            errorDiv.textContent = "⚠️ No puedo conectar con el servidor.";
            chatBody.appendChild(errorDiv);
        }
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Eventos de teclado y click
    chatSend?.addEventListener('click', () => sendMessage());
    chatInput?.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });

    // 4. RECONOCIMIENTO DE VOZ
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition && chatMic) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'es-ES';

        chatMic.addEventListener('click', () => {
            try {
                recognition.start();
                chatMic.style.color = "#ff4444"; 
            } catch (e) {
                console.log("El reconocimiento ya estaba activo");
            }
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            sendMessage(transcript); 
        };

        recognition.onend = () => {
            chatMic.style.color = ""; 
        };
    }

    // 5. ENVÍO DE RESERVAS
    const reservaForm = document.querySelector('.booking-form'); 
    if (reservaForm) {
        reservaForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const datos = {
                origen: document.getElementById('pickup')?.value,
                destino: document.getElementById('destination')?.value,
                fecha_viaje: document.getElementById('date')?.value,
                tipo_servicio: 'estandar',
                monto_total: 25.00
            };

            try {
                const response = await fetch("/create-checkout-session", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(datos)
                });
                const res = await response.json();
                if (res.url) window.location.href = res.url;
            } catch (err) { console.error("Error reserva:", err); }
        });
    }
});

// FUNCIONES GLOBALES
async function toggleFavorite(serviceId) {
    try {
        const response = await fetch(`/api/favoritos/${serviceId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
        if (response.status === 401) {
            window.location.href = "/templates/registro.html";
            return;
        }
        const data = await response.json();
        if (response.ok) {
            const btn = document.querySelector(`button[onclick="toggleFavorite('${serviceId}')"]`);
            const icon = btn?.querySelector('.icon-heart');
            if (icon) icon.textContent = data.message.includes("Añadido") ? "❤️" : "🤍";
        }
    } catch (error) { console.error("Error favoritos:", error); }
}