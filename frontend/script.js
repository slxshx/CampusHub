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
                device.cpu_usage ?? "--";

            const ram =
                device.ram_usage ?? "--";

            const storage =
                device.storage_usage ?? "--";

            const network =
                device.network_usage ?? "--";

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
                            <strong>Storage:</strong>
                            ${storage} %
                        </div>

                        <div>
                            <strong>Netzwerk:</strong>
                            ${network} %
                        </div>

                        <div>
                            <strong>Status:</strong>
                            Aktiv
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