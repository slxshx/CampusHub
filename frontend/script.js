const API_URL = "http://localhost:8000/api/devices";

async function loadDevices() {

    try {

        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("API nicht erreichbar");
        }

        const devices = await response.json();

        const deviceList =
            document.getElementById("geraete-container");

        if (!deviceList) return;

        deviceList.innerHTML = "";

        devices.forEach(device => {

            const cpu =
                device.cpu ?? "--";

            const ram =
                device.ram ?? "--";

            const gpu =
                device.gpu ?? "--";

            deviceList.innerHTML += `

                <div class="device-card">

                    <div class="device-header">
                        ${device.name}
                    </div>

                    <div class="device-body">

                        <div>
                            <strong>Typ:</strong>
                            ${device.device_type}
                        </div>

                        <div>
                            <strong>IP:</strong>
                            ${device.management_ip}
                        </div>
                        <div>
                            <strong>CPU:</strong>
                            ${cpu} %
                        </div>

                        <div>
                            <strong>RAM:</strong>
                            ${ram} %
                        </div>

                        <div>
                            <strong>GPU:</strong>
                            ${gpu} %
                        </div>

                        <div>
                            <strong>Status:</strong>
                            <span class="${device.enabled ? 'status-online' : 'status-offline'}">
                                ${device.enabled ? 'Aktiv' : 'Offline'}
                            </span>
                        </div>

                    </div>

                </div>

            `;

        });

        console.log("Geräte geladen", devices);

    } catch (error) {

        console.error("Fehler:", error);

    }

}

loadDevices();

setInterval(loadDevices, 15000);