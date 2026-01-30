import 'dotenv/config';
import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

// Nota: Es mejor práctica usar process.env.API_KEY, 
// pero mantengo la variable aquí como la tenías.
const API_KEY = "AIzaSyB4klmBe2jLiTLJUh0fnpudxJ22krM5Sko"; 

app.post("/api/ia", async (req, res) => {
    try {
        const { message } = req.body;
        console.log("📩 Mensaje recibido del chat:", message);

        const url = `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=${API_KEY}`;

        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                contents: [{
                    parts: [{ text: "Eres un taxista de Donosti. Responde breve: " + message }]
                }]
            })
        });

        const data = await response.json();

        if (!response.ok) {
            console.error("❌ Error de Google:", data);
            return res.status(500).json({ reply: "Error de API: " + (data.error?.message || "Desconocido") });
        }

        const reply = data.candidates[0].content.parts[0].text;
        res.json({ reply });

    } catch (error) {
        console.error("🔥 Error de servidor:", error);
        res.status(500).json({ reply: "Error interno del servidor." });
    }
});

const PORT = 3000;
app.listen(PORT, () => console.log(`🚀 Servidor activo en http://localhost:${PORT}`));