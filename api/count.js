const { GoogleAuth } = require('google-auth-library');
const { google } = require('googleapis');

// Função para buscar os dados da planilha e fazer as contagens
module.exports = async (req, res) => {
    // --- Adicione estes cabeçalhos CORS no INÍCIO da sua função ---
    res.setHeader('Access-Control-Allow-Origin', 'https://contagem-sj.vercel.app');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS'); // Métodos HTTP permitidos
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type'); // Cabeçalhos permitidos

    // Lidar com requisições OPTIONS (preflight requests)
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    // --- Fim dos cabeçalhos CORS ---

    if (req.method !== 'GET') {
        return res.status(405).json({ message: 'Method Not Allowed' });
    }}

async function getEventData() {
    try {
        const auth = new GoogleAuth({
        credentials: {
        client_email: process.env.GOOGLE_CLIENT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
        },
        scopes: ['https://www.googleapis.com/auth/spreadsheets'],
        });
        
        const sheets = google.sheets({ version: 'v4', auth });

        const spreadsheetId = '1Adp_P2SsQtEtbjZjr0eaDTFQANbc8DrKzU9nWwzXsA4'; // **Substitua pela ID da sua planilha**
        const range = 'Página1!A:Z'; // **Ajuste o range conforme suas colunas e dados**

        const response = await sheets.spreadsheets.values.get({
            spreadsheetId,
            range,
        });

        const rows = response.data.values;
        if (!rows || rows.length === 0) {
            console.log('Nenhum dado encontrado na planilha.');
            return {
                duracaoEvento: 'N/A',
                pessoasImpactadasHoje: 0,
                pessoasImpactadasTotal: 0
            };
        }

        // --- Lógica de contagem (Exemplo baseado em suposições) ---
        // Adapte esta lógica conforme a estrutura real da sua planilha!
        let pessoasImpactadasTotal = 0;
        let pessoasImpactadasHoje = 0;
        let datasEventos = [];

        // Supondo que a primeira linha sejam cabeçalhos e os dados começam da segunda linha
        // E que você tenha uma coluna para 'Data do Evento' e outra para 'Número de Pessoas'
        const headers = rows[0];
        const dataRows = rows.slice(1);

        const dataEventoColIndex = headers.indexOf('Data do Evento'); // Ajuste o nome da coluna
        const numPessoasColIndex = headers.indexOf('Número de Pessoas'); // Ajuste o nome da coluna

        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0); // Zera a hora para comparação de data

        dataRows.forEach(row => {
            const numPessoas = parseInt(row[numPessoasColIndex]) || 0;
            pessoasImpactadasTotal += numPessoas;

            // Se você tiver uma coluna com a data do evento para calcular "pessoas impactadas hoje"
            if (dataEventoColIndex !== -1 && row[dataEventoColIndex]) {
                try {
                    const eventDate = new Date(row[dataEventoColIndex]);
                    eventDate.setHours(0, 0, 0, 0);

                    if (eventDate.getTime() === hoje.getTime()) {
                        pessoasImpactadasHoje += numPessoas;
                    }
                    datasEventos.push(eventDate.getTime());
                } catch (e) {
                    console.warn('Data inválida encontrada:', row[dataEventoColIndex]);
                }
            }
        });

        let duracaoEvento = 'N/A';
        if (datasEventos.length > 1) {
            const minDate = new Date(Math.min(...datasEventos));
            const maxDate = new Date(Math.max(...datasEventos));
            const diffTime = Math.abs(maxDate - minDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            duracaoEvento = `${diffDays + 1} dias`; // +1 para incluir o dia inicial
        } else if (datasEventos.length === 1) {
             duracaoEvento = '1 dia';
        }


        return {
            duracaoEvento: duracaoEvento,
            pessoasImpactadasHoje: pessoasImpactadasHoje,
            pessoasImpactadasTotal: pessoasImpactadasTotal
        };

    } catch (error) {
        console.error('Erro ao buscar dados da planilha:', error.message);
        throw error;
    }
}

// Endpoint para as contagens
app.get('/api/counts', async (req, res) => {
    try {
        const data = await getEventData();
        res.json(data);
    } catch (error) {
        res.status(500).json({ message: 'Erro ao obter os dados do evento', error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
