#!/usr/bin/env python3
"""
centauri_ctl.py — CLI de control para la Elegoo Centauri Carbon vía SDCP WebSocket.
Lee la IP de config/config.toml o de la variable de entorno ELEGOO_PRINTER_IP.
"""

import sys
import os
import json
import uuid
import time
import argparse

# Intentar cargar websockets
try:
    import websockets
    import asyncio
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Intentar cargar tomllib (Python 3.11+) o parseo manual simple
def load_printer_config():
    ip = os.environ.get("ELEGOO_PRINTER_IP", "192.168.1.100")
    port = int(os.environ.get("ELEGOO_WS_PORT", "3030"))
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    candidates = [
        os.path.join(repo_root, "config", "config.toml"),
        os.path.join(repo_root, "config.toml"),
    ]
    
    config_path = next((p for p in candidates if os.path.exists(p)), None)
    if config_path:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ip ="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            ip = val
                    elif line.startswith("sdcp_port ="):
                        val = line.split("=", 1)[1].strip()
                        if val:
                            port = int(val)
        except Exception:
            pass
    return ip, port

CMD = {
    "GET_PRINTER_STATUS": 0,
    "GET_PRINTER_ATTR": 1,
    "SEND_PRINTER_START_PRINT": 128,
    "SEND_PRINTER_SUSPEND_PRINT": 129,
    "SEND_PRINTER_STOP_PRINT": 130,
    "SEND_PRINTER_RESTORE_PRINT": 131,
    "GET_PRINTER_FILE_LIST": 258,
    "EDIT_PRINTER_AXIS_ZERO": 402,
    "EDIT_PRINTER_STATUS_DATA": 403,
}

def make_message(cmd, mainboard_id="", data=None):
    return json.dumps({
        "Id": "",
        "Data": {
            "Cmd": cmd,
            "Data": data or {},
            "RequestID": uuid.uuid4().hex,
            "MainboardID": mainboard_id,
            "TimeStamp": int(time.time()),
            "From": 1
        }
    })

class CentauriClient:
    def __init__(self, ip, port=3030):
        self.ip = ip
        self.port = port
        self.ws_url = f"ws://{ip}:{port}/websocket"
        self.mainboard_id = ""
        self.status = {}
        self.attributes = {}

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, open_timeout=5)
        # Descubrimiento de MainboardID
        msg = make_message(CMD["GET_PRINTER_STATUS"])
        await self.ws.send(msg)
        deadline = time.time() + 3
        while time.time() < deadline:
            try:
                resp = await asyncio.wait_for(self.ws.recv(), timeout=1)
                data = json.loads(resp)
                topic = data.get("Topic", "")
                if "/" in topic:
                    self.mainboard_id = topic.split("/")[-1]
                if "sdcp/status/" in topic:
                    self.status = data.get("Status", {})
                    break
            except Exception:
                break

    async def close(self):
        if hasattr(self, 'ws') and self.ws:
            await self.ws.close()

    async def get_status(self):
        if not self.status:
            msg = make_message(CMD["GET_PRINTER_STATUS"], self.mainboard_id)
            await self.ws.send(msg)
            try:
                resp = await asyncio.wait_for(self.ws.recv(), timeout=2)
                data = json.loads(resp)
                if "sdcp/status/" in data.get("Topic", ""):
                    self.status = data.get("Status", {})
            except Exception:
                pass
        return self.status

    async def set_temperature(self, nozzle=None, bed=None, chamber=None):
        payload = {}
        if nozzle is not None:
            payload["TempTargetNozzle"] = int(nozzle)
        if bed is not None:
            payload["TempTargetHotbed"] = int(bed)
        if chamber is not None:
            payload["TempTargetBox"] = int(chamber)
        
        msg = make_message(CMD["EDIT_PRINTER_STATUS_DATA"], self.mainboard_id, payload)
        await self.ws.send(msg)
        return True

    async def set_light(self, on=True):
        payload = {"Light": 1 if on else 0}
        msg = make_message(CMD["EDIT_PRINTER_STATUS_DATA"], self.mainboard_id, payload)
        await self.ws.send(msg)
        return True

    async def send_command(self, cmd_name):
        if cmd_name in CMD:
            msg = make_message(CMD[cmd_name], self.mainboard_id)
            await self.ws.send(msg)
            return True
        return False

async def run_cli():
    if not HAS_WEBSOCKETS:
        print("❌ Error: Se requiere el paquete 'websockets'.")
        print("Instálalo ejecutando: pip install websockets")
        sys.exit(1)

    ip, port = load_printer_config()

    parser = argparse.ArgumentParser(description="Elegoo Centauri Carbon CLI Controller")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # status
    subparsers.add_parser("status", help="Muestra el estado actual y temperaturas")

    # preheat
    p_heat = subparsers.add_parser("preheat", help="Precalentar boquilla, cama o cámara")
    p_heat.add_argument("--nozzle", type=int, help="Temp boquilla (°C)")
    p_heat.add_argument("--bed", type=int, help="Temp cama (°C)")
    p_heat.add_argument("--chamber", type=int, help="Temp cámara (°C)")

    # light
    p_light = subparsers.add_parser("light", help="Control de luz de cámara")
    p_light.add_argument("state", choices=["on", "off"], help="Encender o apagar luz")

    # pause/resume/stop
    subparsers.add_parser("pause", help="Pausar impresión")
    subparsers.add_parser("resume", help="Reanudar impresión")
    subparsers.add_parser("stop", help="Detener impresión")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    client = CentauriClient(ip, port)
    try:
        print(f"📡 Conectando a Elegoo Centauri Carbon en {ip}:{port}...")
        await client.connect()
        print(f"✅ Conectado. MainboardID: {client.mainboard_id or 'Detectado'}")

        if args.command == "status":
            st = await client.get_status()
            print("\n=== ESTADO DE ELEGOO CENTAURI CARBON ===")
            print(f"Estado de impresión: {st.get('CurrentStatus', ['Desconocido'])}")
            print(f"Boquilla: {st.get('TempCurrentNozzle', 0)}°C (Objetivo: {st.get('TempTargetNozzle', 0)}°C)")
            print(f"Cama:     {st.get('TempCurrentHotbed', 0)}°C (Objetivo: {st.get('TempTargetHotbed', 0)}°C)")
            print(f"Cámara:   {st.get('TempCurrentBox', 0)}°C (Objetivo: {st.get('TempTargetBox', 0)}°C)")
            print(f"Luz:      {'Encendida' if st.get('Light') == 1 else 'Apagada'}")
            print(f"Ventiladores: {st.get('CurrentFanSpeed', {})}")

        elif args.command == "preheat":
            await client.set_temperature(args.nozzle, args.bed, args.chamber)
            print(f"🔥 Comando de precalentamiento enviado (Nozzle: {args.nozzle}, Bed: {args.bed}, Chamber: {args.chamber})")

        elif args.command == "light":
            await client.set_light(args.state == "on")
            print(f"💡 Luz {'encendida' if args.state == 'on' else 'apagada'}")

        elif args.command == "pause":
            await client.send_command("SEND_PRINTER_SUSPEND_PRINT")
            print("⏸️ Impresión pausada.")
        elif args.command == "resume":
            await client.send_command("SEND_PRINTER_RESTORE_PRINT")
            print("▶️ Impresión reanudada.")
        elif args.command == "stop":
            await client.send_command("SEND_PRINTER_STOP_PRINT")
            print("⏹️ Impresión detenida.")

    except Exception as e:
        print(f"⚠️ No se pudo comunicar con la impresora ({ip}:{port}): {e}")
        print("Verifica que la impresora esté encendida y conectada a la misma red local.")
    finally:
        await client.close()

if __name__ == "__main__":
    if HAS_WEBSOCKETS:
        asyncio.run(run_cli())
    else:
        print("❌ Error: Falta librería websockets. Instálala con 'pip install websockets'.")
