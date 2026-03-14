const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const useLlmToggle = document.getElementById('useLlmToggle');
const loadingState = document.getElementById('loading');
const resultsContainer = document.getElementById('resultsContainer');
const aiAnswerBlock = document.getElementById('aiAnswerBlock');
const aiContent = document.getElementById('aiContent');
const documentResults = document.getElementById('documentResults');
const timeStats = document.getElementById('timeStats');

// Event Listeners
searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) return;

    // Show loading
    loadingState.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    
    // Clear previous
    aiContent.innerHTML = '';
    documentResults.innerHTML = '';

    const useLlm = useLlmToggle.checked;

    try {
        const response = await fetch('http://localhost:8000/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: 4,
                use_llm: useLlm
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data, useLlm);

    } catch (error) {
        console.error('Lỗi khi gọi API:', error);
        aiContent.innerHTML = '<p style="color: red;">Đã có lỗi xảy ra khi gọi API. Vui lòng bật Terminal chạy `uvicorn api.main:app --reload`</p>';
        aiAnswerBlock.style.display = 'block';
        loadingState.classList.add('hidden');
        resultsContainer.classList.remove('hidden');
    }
}

function displayResults(data, useLlm) {
    // Hide loading
    loadingState.classList.add('hidden');
    resultsContainer.classList.remove('hidden');

    // 1. Render AI Answer
    if (useLlm && data.answer) {
        aiAnswerBlock.style.display = 'block';
        // Use Marked.js to parse markdown
        aiContent.innerHTML = marked.parse(data.answer);
    } else {
        aiAnswerBlock.style.display = 'none';
    }

    // 2. Render Documents
    timeStats.textContent = `⚡ Sinh viên query mất: ${data.total_time_ms}ms`;
    
    if (data.results && data.results.length > 0) {
        data.results.forEach(doc => {
            const card = document.createElement('a');
            card.href = doc.url;
            card.className = 'doc-card';
            card.target = '_blank';
            
            card.innerHTML = `
                <span class="doc-category">${doc.category}</span>
                <h4 class="doc-title">${doc.title}</h4>
                <p class="doc-snippet">${doc.snippet}</p>
            `;
            
            documentResults.appendChild(card);
        });
    } else {
        documentResults.innerHTML = '<p>Không tìm thấy tài liệu phù hợp.</p>';
    }
}
