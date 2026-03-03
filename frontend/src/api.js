const API_BASE_URL = 'http://localhost:8000/api';
const DEFAULT_FARMER_ID = 'default-farmer-id';

export const sendChat = async (message) => {
    const response = await fetch(`${API_BASE_URL}/orchestrator/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ farmer_id: DEFAULT_FARMER_ID, message })
    });
    if (!response.ok) throw new Error('Failed to communicate with AI Advisory');
    return response.json();
};

export const fetchSoilHealth = async (shcNumber) => {
    const response = await fetch(`${API_BASE_URL}/shc/fetch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ farmer_id: DEFAULT_FARMER_ID, shc_id: shcNumber })
    });
    if (!response.ok) throw new Error('Failed to fetch SHC profile');
    return response.json();
};

export const analyzeHarvest = async (data) => {
    const payload = { ...data, farmer_id: DEFAULT_FARMER_ID };
    const response = await fetch(`${API_BASE_URL}/harvest/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('Failed to analyze harvest scenarios');
    return response.json();
};

export const uploadScannerImage = async (file, isPesticide) => {
    const formData = new FormData();
    formData.append('file', file);
    // Usually farmer_id goes as a form field if the backend expects it, but since vision endpoint 
    // expects it too, let's append it
    formData.append('farmer_id', DEFAULT_FARMER_ID);

    const endpoint = isPesticide ? '/pesticide/verify' : '/vision/detect';
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) throw new Error('Failed to analyze image');
    return response.json();
};

export const generateSustainabilityReport = async () => {
    const response = await fetch(`${API_BASE_URL}/report/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ farmer_id: DEFAULT_FARMER_ID })
    });
    if (!response.ok) throw new Error('Failed to generate report');
    return response.blob();
};
