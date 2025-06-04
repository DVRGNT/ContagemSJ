// Em script.js (hospedado no Vercel)

const eventDurationElement = document.getElementById('event-duration');
const impactedTodayElement = document.getElementById('impacted-today');
const impactedTotalElement = document.getElementById('impacted-total');

// URL do seu backend no PythonAnywhere
const apiUrl = 'https://SEU_USERNAME.pythonanywhere.com/api/impact-data'; // Use HTTPS

// --- Lógica do Temporizador (como antes) ---
const eventStartDate = new Date('2025-01-01T00:00:00Z'); // Sua data de início
function updateEventDuration() {
    const now = new Date();
    const diffMs = now - eventStartDate;
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);
    eventDurationElement.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
}
setInterval(updateEventDuration, 1000);
updateEventDuration();

// --- Lógica para Buscar Dados da Planilha (do Backend) ---
async function fetchData() {
    console.log("Buscando dados atualizados...");
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            // Se o backend retornar um erro específico, podemos tratar
            if (response.status === 500) {
                const errorData = await response.json();
                console.error("Erro do servidor ao buscar dados:", errorData.error || "Erro desconhecido");
                impactedTodayElement.textContent = "Erro";
                impactedTotalElement.textContent = "Erro";
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        impactedTodayElement.textContent = data.impactedToday.toLocaleString('pt-BR');
        impactedTotalElement.textContent = data.impactedTotal.toLocaleString('pt-BR');

    } catch (error) {
        console.error("Erro ao buscar dados:", error);
        impactedTodayElement.textContent = "Erro"; // Mantém "Erro" se a busca falhar
        impactedTotalElement.textContent = "Erro";
    }
}

// Busca os dados quando a página carrega
fetchData();

// ATUALIZA OS DADOS A CADA 5 MINUTOS (300000 milissegundos)
setInterval(fetchData, 5 * 60 * 1000);