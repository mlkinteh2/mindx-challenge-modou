// API Configuration
const API_BASE_URL = 'http://localhost:8001';

// State Management
let fleetData = {
    summary: null,
    vessels: [],
    surplusVessels: [],
    deficitVessels: [],
    optimalPools: []
};

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Initializing MIND X Dashboard...');

    // Check API health
    const isHealthy = await checkAPIHealth();

    if (isHealthy) {
        await loadDashboardData();
    } else {
        showError('Unable to connect to API. Please ensure the backend server is running.');
    }

    // Setup event listeners
    setupEventListeners();
});

// Check API Health
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('✅ API Health:', data);
        return data.status === 'healthy';
    } catch (error) {
        console.error('❌ API Health Check Failed:', error);
        return false;
    }
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        // Load compliance summary
        await loadComplianceSummary();

        // Load vessels
        await loadVessels();

        // Load optimal pools
        await loadOptimalPools();

        console.log('✅ Dashboard data loaded successfully');
    } catch (error) {
        console.error('❌ Error loading dashboard data:', error);
        showError('Error loading dashboard data. Please try again.');
    }
}

// Load Compliance Summary
async function loadComplianceSummary() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/compliance/summary`);
        const data = await response.json();

        fleetData.summary = data;

        // Update stats cards
        document.getElementById('total-vessels').textContent = data.total_vessels;
        document.getElementById('surplus-vessels').textContent = data.surplus_vessels;
        document.getElementById('deficit-vessels').textContent = data.deficit_vessels;
        document.getElementById('financial-impact').textContent = formatCurrency(data.total_financial_impact);

        // Create liability chart
        createLiabilityChart(data);

    } catch (error) {
        console.error('Error loading compliance summary:', error);
    }
}

// Load Vessels
async function loadVessels() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/vessels`);
        const data = await response.json();

        fleetData.vessels = data.vessels;
        fleetData.surplusVessels = data.vessels.filter(v => v.compliance_status === 'Surplus');
        fleetData.deficitVessels = data.vessels.filter(v => v.compliance_status === 'Deficit');

        // Render vessels grid
        renderVesselsGrid(data.vessels);

        // Populate vessel selectors
        populateVesselSelectors();

    } catch (error) {
        console.error('Error loading vessels:', error);
    }
}

// Load Optimal Pools
async function loadOptimalPools() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/pooling/optimal?max_pools=5`);
        const data = await response.json();

        fleetData.optimalPools = data.optimal_pools;

        // Render optimal pools
        renderOptimalPools(data.optimal_pools);

    } catch (error) {
        console.error('Error loading optimal pools:', error);
    }
}

// Create Liability Chart
function createLiabilityChart(summary) {
    const ctx = document.getElementById('liabilityChart').getContext('2d');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Surplus Vessels', 'Deficit Vessels'],
            datasets: [{
                data: [summary.surplus_vessels, summary.deficit_vessels],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 14,
                            family: 'Inter'
                        },
                        padding: 20
                    }
                },
                title: {
                    display: true,
                    text: 'Fleet Compliance Distribution',
                    font: {
                        size: 18,
                        weight: 'bold',
                        family: 'Inter'
                    },
                    padding: 20
                }
            }
        }
    });
}

// Render Vessels Grid
function renderVesselsGrid(vessels) {
    const grid = document.getElementById('vessels-grid');
    grid.innerHTML = '';

    // Show only first 12 vessels for performance
    const displayVessels = vessels.slice(0, 12);

    displayVessels.forEach(vessel => {
        const card = createVesselCard(vessel);
        grid.appendChild(card);
    });
}

// Create Vessel Card
function createVesselCard(vessel) {
    const card = document.createElement('div');
    card.className = `vessel-card ${vessel.compliance_status.toLowerCase()} fade-in`;

    card.innerHTML = `
        <div class="vessel-header">
            <div class="vessel-id">${vessel.ship_id}</div>
            <div class="vessel-badge ${vessel.compliance_status.toLowerCase()}">
                ${vessel.compliance_status}
            </div>
        </div>
        <div class="vessel-type">${vessel.ship_type}</div>
        <div class="vessel-metrics">
            <div class="metric-row">
                <span class="metric-label">GHG Intensity</span>
                <span class="metric-value">${vessel.ghg_intensity.toFixed(2)} gCO₂/mile</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Compliance Balance</span>
                <span class="metric-value">${vessel.compliance_balance.toFixed(2)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Financial Impact</span>
                <span class="metric-value">${formatCurrency(vessel.financial_impact)}</span>
            </div>
        </div>
    `;

    return card;
}

// Populate Vessel Selectors
function populateVesselSelectors() {
    const vessel1Select = document.getElementById('vessel1');
    const vessel2Select = document.getElementById('vessel2');

    // Clear existing options
    vessel1Select.innerHTML = '<option value="">Select a deficit vessel...</option>';
    vessel2Select.innerHTML = '<option value="">Select a surplus vessel...</option>';

    // Populate deficit vessels
    fleetData.deficitVessels.forEach(vessel => {
        const option = document.createElement('option');
        option.value = vessel.ship_id;
        option.textContent = `${vessel.ship_id} - ${vessel.ship_type}`;
        vessel1Select.appendChild(option);
    });

    // Populate surplus vessels
    fleetData.surplusVessels.forEach(vessel => {
        const option = document.createElement('option');
        option.value = vessel.ship_id;
        option.textContent = `${vessel.ship_id} - ${vessel.ship_type}`;
        vessel2Select.appendChild(option);
    });
}

// Render Optimal Pools
function renderOptimalPools(pools) {
    const list = document.getElementById('optimal-pools-list');
    list.innerHTML = '';

    if (pools.length === 0) {
        list.innerHTML = '<p style="text-align: center; color: var(--gray);">No optimal pooling opportunities found.</p>';
        return;
    }

    pools.forEach((pool, index) => {
        const item = document.createElement('div');
        item.className = 'pool-item fade-in';
        item.style.animationDelay = `${index * 0.1}s`;

        item.innerHTML = `
            <div class="pool-header">
                <div class="pool-vessels">
                    <strong>${pool.vessel1_id}</strong> + <strong>${pool.vessel2_id}</strong>
                </div>
                <div class="pool-savings">💰 ${formatCurrency(pool.savings)}</div>
            </div>
            <div class="pool-details">
                <div>
                    <strong>Status:</strong> ${pool.pooling_successful ? '✅ Successful' : '❌ Failed'}
                </div>
                <div>
                    <strong>Weighted Intensity:</strong> ${pool.weighted_intensity.toFixed(2)} gCO₂/mile
                </div>
                <div>
                    <strong>Target:</strong> ${pool.target_intensity.toFixed(2)} gCO₂/mile
                </div>
            </div>
        `;

        list.appendChild(item);
    });
}

// Setup Event Listeners
function setupEventListeners() {
    // Vessel selection change handlers
    document.getElementById('vessel1').addEventListener('change', (e) => {
        updateVesselInfo('vessel1', e.target.value);
    });

    document.getElementById('vessel2').addEventListener('change', (e) => {
        updateVesselInfo('vessel2', e.target.value);
    });

    // Simulate pooling button
    document.getElementById('simulate-btn').addEventListener('click', simulatePooling);

    // Smooth scrolling for nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });

                // Update active nav link
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            }
        });
    });
}

// Update Vessel Info
function updateVesselInfo(vesselInputId, vesselId) {
    const infoDiv = document.getElementById(`${vesselInputId}-info`);

    if (!vesselId) {
        infoDiv.innerHTML = '';
        return;
    }

    const vessel = fleetData.vessels.find(v => v.ship_id === vesselId);

    if (vessel) {
        infoDiv.innerHTML = `
            <div><strong>Type:</strong> ${vessel.ship_type}</div>
            <div><strong>GHG Intensity:</strong> ${vessel.ghg_intensity.toFixed(2)} gCO₂/mile</div>
            <div><strong>Balance:</strong> ${vessel.compliance_balance.toFixed(2)}</div>
        `;
    }
}

// Simulate Pooling
async function simulatePooling() {
    const vessel1Id = document.getElementById('vessel1').value;
    const vessel2Id = document.getElementById('vessel2').value;

    if (!vessel1Id || !vessel2Id) {
        alert('Please select both vessels for pooling simulation.');
        return;
    }

    const btn = document.getElementById('simulate-btn');
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width: 20px; height: 20px; border-width: 2px;"></div> Simulating...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/pooling`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vessel1_id: vessel1Id,
                vessel2_id: vessel2Id
            })
        });

        const result = await response.json();

        // Display result
        displayPoolingResult(result);

    } catch (error) {
        console.error('Error simulating pooling:', error);
        alert('Error simulating pooling. Please try again.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor">
                <path d="M10 2V18M10 18L16 12M10 18L4 12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Simulate Pooling
        `;
    }
}

// Display Pooling Result
function displayPoolingResult(result) {
    const resultDiv = document.getElementById('pooling-result');
    const isSuccess = result.pooling_successful;

    resultDiv.className = `pooling-result ${isSuccess ? 'success' : 'failure'}`;

    resultDiv.innerHTML = `
        <div class="result-header">
            <div class="result-icon ${isSuccess ? 'success' : 'failure'}">
                ${isSuccess ? '✓' : '✗'}
            </div>
            <div>
                <div class="result-title">
                    ${isSuccess ? 'Pooling Successful!' : 'Pooling Not Compliant'}
                </div>
                <p style="color: var(--gray); margin-top: 0.5rem;">
                    ${isSuccess
            ? 'The combined pool meets the 2026 target intensity.'
            : 'The combined pool still exceeds the target intensity.'}
                </p>
            </div>
        </div>
        
        <div class="result-metrics">
            <div class="result-metric">
                <div class="result-metric-label">Weighted Intensity</div>
                <div class="result-metric-value">${result.weighted_intensity.toFixed(2)}</div>
                <div style="font-size: 0.75rem; color: var(--gray); margin-top: 0.25rem;">gCO₂/mile</div>
            </div>
            
            <div class="result-metric">
                <div class="result-metric-label">Target Intensity</div>
                <div class="result-metric-value">${result.target_intensity.toFixed(2)}</div>
                <div style="font-size: 0.75rem; color: var(--gray); margin-top: 0.25rem;">gCO₂/mile</div>
            </div>
            
            <div class="result-metric">
                <div class="result-metric-label">Combined Balance</div>
                <div class="result-metric-value" style="color: ${result.combined_balance < 0 ? 'var(--success)' : 'var(--danger)'};">
                    ${result.combined_balance < 0 ? 'Surplus: ' : 'Deficit: '}
                    ${Math.abs(result.combined_balance).toFixed(2)}
                </div>
                <div style="font-size: 0.75rem; color: var(--gray); margin-top: 0.25rem;">gCO₂/mile</div>
            </div>
            
            <div class="result-metric">
                <div class="result-metric-label">Potential Savings</div>
                <div class="result-metric-value" style="color: var(--success);">${formatCurrency(result.savings)}</div>
                <div style="font-size: 0.75rem; color: var(--gray); margin-top: 0.25rem;">USD</div>
            </div>
        </div>
    `;

    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Utility Functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function showError(message) {
    const main = document.querySelector('.main');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        background: rgba(239, 68, 68, 0.1);
        border: 2px solid var(--danger);
        border-radius: var(--radius);
        padding: 2rem;
        text-align: center;
        color: var(--danger);
        font-weight: 600;
        margin: 2rem 0;
    `;
    errorDiv.textContent = message;
    main.insertBefore(errorDiv, main.firstChild);
}

// Export for debugging
window.fleetData = fleetData;
window.API_BASE_URL = API_BASE_URL;
