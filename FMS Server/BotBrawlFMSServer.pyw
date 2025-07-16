import json
import threading
import time
import socket
import serial
import serial.tools.list_ports
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import sys
import os
import requests
import websocket
import queue

# === CONFIG ===
TIMER_DURATION = 180
TIMER_FILE = "timer1.txt"
TIMER_FILE_2 = "timer2.txt"
UDP_PORT = 9876
ARDUINO_VID, ARDUINO_PID = 0x2341, 0x8036  # Change to your Arduino's VID/PID

# === GLOBALS ===
state = {"status": "ready", "remaining": TIMER_DURATION}
state2 = {"status": "ready", "remaining": TIMER_DURATION}
lock = threading.Lock()
stop_event = threading.Event()
ser = None
ws = None
action_queue = queue.Queue()

def write_timer_file():
    val = state["remaining"]
    txt = f"{val // 60}:{val % 60:02}" if val >= 60 else str(val)
    try:
        with open(TIMER_FILE, "w", encoding="utf-8") as f:
            f.write(txt)
    except Exception as e:
        print(f"Error writing timer file: {e}")

def write_timer_file2():
    val = state2["remaining"]
    txt = f"{val // 60}:{val % 60:02}" if val >= 60 else str(val)
    try:
        with open(TIMER_FILE_2, "w", encoding="utf-8") as f:
            f.write(txt)
    except Exception as e:
        print(f"Error writing timer2 file: {e}")

def timer_loop():
    print("⏱ Timer loop started.")
    while not stop_event.is_set():
        time.sleep(1)
        with lock:
            if state["status"] == "running" and state["remaining"] > 0:
                state["remaining"] -= 1
                write_timer_file()
            elif state["status"] == "running" and state["remaining"] == 0:
                # Timer reached zero, stop counting down and stay at 0
                state["status"] = "paused"  # or keep "running" but no countdown
                write_timer_file()


def timer_loop2():
    print("⏱ Timer loop 2 started.")
    while not stop_event.is_set():
        time.sleep(1)
        with lock:
            if state2["status"] == "running" and state2["remaining"] > 0:
                state2["remaining"] -= 1
                write_timer_file2()
            elif state2["status"] == "running" and state2["remaining"] == 0:
                state2["status"] = "paused"
                write_timer_file2()


def websocket_handler():
    global ws
    print("🌐 WebSocket handler started.")

    def on_open(websocket):
        print("✓ WebSocket connected to Streamer.bot")

    def on_error(websocket, error):
        print(f"⚠ WebSocket error: {error}")

    def on_close(websocket, close_status_code, close_msg):
        print("⚠ WebSocket connection closed")

    while not stop_event.is_set():
        try:
            print("Connecting to Streamer.bot WebSocket...")
            ws = websocket.WebSocketApp(
                "ws://127.0.0.1:8080/",
                on_open=on_open,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print(f"WebSocket connection failed: {e}")

        if not stop_event.is_set():
            print("Retrying WebSocket connection in 5 seconds...")
            time.sleep(5)

def action_sender():
    print("🎯 Action sender started.")
    while not stop_event.is_set():
        try:
            action_name = action_queue.get(timeout=1)
            if ws and hasattr(ws, 'sock') and ws.sock and ws.sock.connected:
                message = {
                    "request": "DoAction",
                    "action": {
                        "name": action_name
                    },
                    "args": {
                        "source": "arduino_button"
                    },
                    "id": f"arduino_{int(time.time() * 1000)}"
                }
                ws.send(json.dumps(message))
                print(f"⚡ Sent via WebSocket: {action_name}")
            else:
                print(f"⚠ WebSocket not connected, skipping: {action_name}")
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Action send error: {e}")

def find_arduino():
    for port in serial.tools.list_ports.comports():
        try:
            if port.vid == ARDUINO_VID and port.pid == ARDUINO_PID:
                return port.device
        except AttributeError:
            continue
    return None

def arduino_listener():
    global ser
    print("🎛 Arduino listener started.")
    while not stop_event.is_set():
        port = find_arduino()
        if not port:
            print("Arduino not found. Retrying in 2 sec...")
            time.sleep(2)
            continue
        try:
            ser = serial.Serial(port, 115200, timeout=0.1)
            print(f"Connected to Arduino on {port}")
            while ser.is_open and not stop_event.is_set():
                try:
                    line = ser.readline().decode().strip()
                    if line:
                        print(f"Arduino said: {line}")
                        button_mappings = {
                            # Arena 1
                            "ButtonA0 pressed": "RedButtonArena1",
                            "ButtonA1 pressed": "WhiteButtonArena1",
                            # Arena 2
                            "ButtonA2 pressed": "RedButtonArena2",
                            "ButtonA3 pressed": "WhiteButtonArena2",
                            "a0": "RedButtonArena1",
                            "a1": "WhiteButtonArena1",
                            "a2": "RedButtonArena2",
                            "a3": "WhiteButtonArena2",
                            "RedButtonArena1": "RedButtonArena1",
                            "WhiteButtonArena1": "WhiteButtonArena1",
                            "RedButtonArena2": "RedButtonArena2",
                            "WhiteButtonArena2": "WhiteButtonArena2"
                        }

                        button_name = button_mappings.get(line)
                        if button_name:
                            print(f"Button: {line} → {button_name}")
                            action_queue.put(button_name)
                except Exception as e:
                    print(f"Serial read error: {e}")
                    break
        except Exception as e:
            print(f"Error opening serial port: {e}")
        try:
            if ser:
                ser.close()
        except:
            pass
        time.sleep(2)

def udp_server():
    global ser
    print("📡 UDP server started.")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", UDP_PORT))
    sock.settimeout(1)
    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            cmd = data.decode().strip()
            print(f"UDP received: {cmd} from {addr}")

            def safe_sendto(data, address):
                try:
                    sock.sendto(data, address)
                except (ConnectionResetError, OSError) as e:
                    print(f"Client {address} disconnected before response: {e}")
                except Exception as e:
                    print(f"Failed to send UDP response to {address}: {e}")

            with lock:
                # Arena 1
                if cmd == "start":
                    state["status"] = "running"
                    safe_sendto(b"Timer started", addr)
                elif cmd == "pause":
                    state["status"] = "paused"
                    safe_sendto(b"Timer paused", addr)
                elif cmd == "reset":
                    state.update({"status": "ready", "remaining": TIMER_DURATION})
                    write_timer_file()
                    safe_sendto(b"Timer reset", addr)
                elif cmd == "status":
                    safe_sendto(json.dumps(state).encode(), addr)
                # Arena 2
                elif cmd == "start2":
                    state2["status"] = "running"
                    safe_sendto(b"Arena 2 timer started", addr)
                elif cmd == "pause2":
                    state2["status"] = "paused"
                    safe_sendto(b"Arena 2 timer paused", addr)
                elif cmd == "reset2":
                    state2.update({"status": "ready", "remaining": TIMER_DURATION})
                    write_timer_file2()
                    safe_sendto(b"Arena 2 timer reset", addr)
                elif cmd == "status2":
                    safe_sendto(json.dumps(state2).encode(), addr)
                # Forward to Arduino if connected
                elif ser and ser.is_open:
                    try:
                        ser.write((cmd + "\n").encode())
                        time.sleep(0.05)
                        resp = ser.readline().decode().strip()
                        safe_sendto((resp or "No response").encode(), addr)
                    except Exception as e:
                        safe_sendto(f"Arduino error: {e}".encode(), addr)
                else:
                    safe_sendto(b"Unknown command or Arduino not connected", addr)

        except socket.timeout:
            continue
        except Exception as e:
            print(f"UDP server error: {e}")

def make_tray():
    def quit_app(icon, item):
        stop_event.set()
        try:
            if ser:
                ser.close()
        except:
            pass
        icon.stop()
        os._exit(0)

    def restart(icon, item):
        stop_event.set()
        icon.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    img = Image.new("RGB", (64, 64), "white")
    ImageDraw.Draw(img).rectangle((8, 8, 56, 56), outline="black", fill="green")
    return Icon("FMS", img, "FMS Timer", Menu(
        MenuItem("Restart", restart),
        MenuItem("Quit", quit_app)
    ))

if __name__ == "__main__":
    print("🚦 Starting FMS server...")
    write_timer_file()
    write_timer_file2()
    threading.Thread(target=timer_loop, daemon=True).start()
    threading.Thread(target=timer_loop2, daemon=True).start()
    threading.Thread(target=udp_server, daemon=True).start()
    threading.Thread(target=arduino_listener, daemon=True).start()
    threading.Thread(target=websocket_handler, daemon=True).start()
    threading.Thread(target=action_sender, daemon=True).start()
    tray = make_tray()
    threading.Thread(target=tray.run, daemon=True).start()
    while not stop_event.is_set():
        print("💓 Main loop heartbeat: still running...")
        time.sleep(5)
