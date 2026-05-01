const HEALTH_URL = "http://127.0.0.1:8000/health";

const checkHealthBtn = document.getElementById("check-health-btn");
const healthOutput = document.getElementById("health-output");

async function checkBackendHealth() {
  healthOutput.textContent = "Checking backend...";

  try {
    const response = await fetch(HEALTH_URL);
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    const data = await response.json();
    healthOutput.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    healthOutput.textContent = `Connection failed: ${error.message}`;
  }
}

checkHealthBtn.addEventListener("click", checkBackendHealth);
