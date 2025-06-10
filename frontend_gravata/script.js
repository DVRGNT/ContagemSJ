// Em script.js (hospedado no Vercel)

// Elementos do DOM
const impactedTodayElement = document.getElementById('impacted-today');
const impactedTotalElement = document.getElementById('impacted-total');
const peakHourElement = document.getElementById('peak-hour'); // Novo elemento
const topZoneElement = document.getElementById('top-zone');     // Novo elemento

// URL do seu backend no PythonAnywhere
const apiUrl = 'https://gravata.visionariadivergente.space/api/impact-data';

// --- Lógica do Temporizador REMOVIDA ---

// --- Lógica para Buscar Dados da Planilha (do Backend) ---
async function fetchData() {
    console.log("Buscando dados atualizados...");
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Atualiza os elementos com os dados recebidos da API
        impactedTodayElement.textContent = data.impactedToday.toLocaleString('pt-BR');
        impactedTotalElement.textContent = data.impactedTotal.toLocaleString('pt-BR');
        peakHourElement.textContent = data.peakHour;
        topZoneElement.textContent = data.topZoneByPeople;

    } catch (error) {
        console.error("Erro ao buscar dados:", error);
        // Define texto de erro para todos os campos se a busca falhar
        impactedTodayElement.textContent = "Erro";
        impactedTotalElement.textContent = "Erro";
        peakHourElement.textContent = "Erro";
        topZoneElement.textContent = "Erro";
    }
}

// Busca os dados quando a página carrega
fetchData();

// ATUALIZA OS DADOS A CADA 5 MINUTOS (ou o intervalo que preferir)
setInterval(fetchData, 1 * 60 * 1000);