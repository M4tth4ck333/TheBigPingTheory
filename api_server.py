# Datei: api_server.py
from flask import Flask, request, jsonify
from engine import DurgaEngine, QemuVM # Annahme: Du hast deine Klassen modularisiert
import threading

app = Flask(__name__)
# Die Engine global instanziieren
durga_engine = DurgaEngine()
# Beispiel-VM hinzufügen (Pfad anpassen!)
# vm = QemuVM("bot1", "/pfad/zu/deinem/image.qcow2")
# durga_engine.add_qemu_vm(vm)

@app.route("/api/vms/start", methods=["POST"])
def start_vms():
    # Starte die VMs in einem separaten Thread, damit der API-Aufruf sofort zurückkehrt
    threading.Thread(target=durga_engine.start_all_vms).start()
    return jsonify({"status": "starting all vms"}), 202

@app.route("/api/vms/stop", methods=["POST"])
def stop_vms():
    threading.Thread(target=durga_engine.stop_all_vms).start()
    return jsonify({"status": "stopping all vms"}), 202

@app.route("/api/vms/status", methods=["GET"])
def get_vm_status():
    status_list = [
        {"name": vm.name, "is_running": vm.is_running()}
        for vm in durga_engine.qemu_vms
    ]
    return jsonify(status_list)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
