import os
import datetime
from flask import Flask, request, jsonify
import requests
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "licenciasbot2024")
PAGE_ID = os.environ.get("PAGE_ID", "")

# ─── CONTENIDO DEL BOT ────────────────────────────────────────────

PRODUCTOS = """
Licencias disponibles - Bolivia

1 Windows 10 Home           - Bs. 50
2 Windows 10 Pro            - Bs. 40
3 Windows 11 Home           - Bs. 50
4 Windows 11 Pro            - Bs. 45
5 Office 2024 Pro Plus      - Bs. 50
6 Office 2021 Pro Plus      - Bs. 50
7 Office 2019 Pro Plus      - Bs. 50
8 Office 2016 Pro Plus      - Bs. 50
9 Paquete Win 11 Pro + Office 2024/2021/2019/2016 - Bs. 70

Entrega inmediata por WhatsApp
Activacion garantizada o te devuelvo el dinero
"""

MENU_PRINCIPAL = """
Hola! Bienvenido a LicenciasBolivia

Que necesitas hoy?

A - Ver productos y precios
B - Como funciona la compra?
C - Hablar con un asesor
D - Garantia y soporte

Responde con la letra de tu opcion
"""

COMO_FUNCIONA = """
Como comprar en 3 pasos simples:

Paso 1 - Elige tu producto y escribenos el numero
Paso 2 - Te enviamos el QR de pago (Bs. exactos)
Paso 3 - Confirmas el pago y recibes tu licencia en minutos

Tiempo de entrega: 5-15 minutos
Disponible: Lunes a Sabado 8am - 9pm

Listo para comprar? Escribe el numero del producto!
"""

GARANTIA = """
Nuestra garantia:

Si tu licencia no activa correctamente te la cambiamos sin costo
Si el problema persiste te devolvemos tu dinero
Soporte por WhatsApp incluido

Para continuar escribe A para ver productos o C para hablar con un asesor
"""

# ─── POSTS AUTOMÁTICOS DIARIOS ────────────────────────────────────

POSTS = [
    # Lunes - Windows 11 Pro
    """Windows 11 Pro ORIGINAL - Bs. 45

La version mas completa de Windows para tu PC o laptop.
Activacion permanente, sin mensualidades.

Entrega en 5-15 minutos por WhatsApp
Garantia de activacion incluida

Escribenos ahora: wa.me/59174222062
o por Messenger""",

    # Martes - Office 2024
    """Office 2024 Professional Plus - Bs. 50

Word, Excel, PowerPoint, Outlook y mucho mas.
Licencia original con activacion permanente.

Sin suscripcion mensual, pagas una sola vez.
Entrega inmediata por WhatsApp

Escribenos: wa.me/59174222062""",

    # Miercoles - Paquete completo
    """PAQUETE COMPLETO - Bs. 70

Windows 11 Pro + Office 2024/2021/2019/2016 Pro

Todo lo que necesitas para tu PC en un solo paquete.
Ahorra comprando los dos juntos.

Entrega en minutos - Garantia incluida
Escribenos: wa.me/59174222062""",

    # Jueves - Windows 10
    """Windows 10 Pro ORIGINAL - Bs. 40

Compatible con todos los equipos.
Perfecto si tu PC no soporta Windows 11.

Activacion permanente garantizada.
Entrega inmediata por WhatsApp

Escribenos: wa.me/59174222062""",

    # Viernes - Office 2021
    """Office 2021 Pro Plus ORIGINAL - Bs. 50

La version clasica de Office sin suscripcion.
Word, Excel, PowerPoint y mucho mas.

Una sola compra, usas para siempre.
Entrega en 5-15 minutos

Escribenos: wa.me/59174222062""",

    # Sabado - Garantia y confianza
    """Por que comprar con nosotros?

Licencias 100% originales y verificadas
Entrega en 5-15 minutos por WhatsApp
Si no activa te cambiamos sin costo
Soporte incluido despues de la compra
Mas de 100 clientes satisfechos en Bolivia

Consulta sin compromiso:
wa.me/59174222062""",

    # Domingo - Todos los productos
    """Nuestro catalogo completo de licencias:

Windows 10 Home - Bs. 50
Windows 10 Pro  - Bs. 40
Windows 11 Home - Bs. 50
Windows 11 Pro  - Bs. 45
Office 2024 Pro Plus - Bs. 50
Office 2021 Pro Plus - Bs. 50
Office 2019 Pro Plus - Bs. 50
Office 2016 Pro Plus - Bs. 50
Paquete Win 11 + Office - Bs. 70

Entrega inmediata - Garantia incluida
Escribenos: wa.me/59174222062""",
]

def publicar_post_diario():
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        return
    dia = datetime.datetime.now().weekday()  # 0=lunes, 6=domingo
    mensaje = POSTS[dia]
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
    payload = {"message": mensaje, "access_token": PAGE_ACCESS_TOKEN}
    requests.post(url, data=payload)

# ─── MESSENGER BOT ────────────────────────────────────────────────

def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v19.0/me/messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    requests.post(url, headers=headers, json=payload, params=params)

def handle_message(sender_id, message_text):
    text = message_text.strip().lower()

    saludos = ["hola", "buenos dias", "buenas", "hello", "hi", "buenas tardes", "buenas noches", "hey"]
    if any(s in text for s in saludos) or text in ["inicio", "menu", "start"]:
        send_message(sender_id, MENU_PRINCIPAL)
        return

    if text in ["a", "ver productos", "precios", "productos", "comprar"]:
        send_message(sender_id, PRODUCTOS)
        send_message(sender_id, "Escribe el NUMERO del producto que quieres comprar (del 1 al 9)")
        return

    if text in ["b", "como funciona", "como comprar"]:
        send_message(sender_id, COMO_FUNCIONA)
        return

    if text in ["c", "asesor", "hablar", "contacto"]:
        send_message(sender_id, "Te conectamos con un asesor ahora mismo!\n\nEscribenos directo por WhatsApp:\nhttps://wa.me/59174222062\n\nO si prefieres, deja tu consulta aqui y te respondemos en minutos.")
        return

    if text in ["d", "garantia", "soporte"]:
        send_message(sender_id, GARANTIA)
        return

    productos_map = {
        "1": ("Windows 10 Home", "Bs. 50"),
        "2": ("Windows 10 Pro", "Bs. 40"),
        "3": ("Windows 11 Home", "Bs. 50"),
        "4": ("Windows 11 Pro", "Bs. 45"),
        "5": ("Office 2024 Professional Plus", "Bs. 50"),
        "6": ("Office 2021 Pro Plus", "Bs. 50"),
        "7": ("Office 2019 Pro Plus", "Bs. 50"),
        "8": ("Office 2016 Pro Plus", "Bs. 50"),
        "9": ("Paquete Win 11 Pro + Office 2024/2021/2019/2016 Pro", "Bs. 70"),
    }

    if text in productos_map:
        nombre, precio = productos_map[text]
        respuesta = f"Excelente eleccion!\n\nProducto: {nombre}\nPrecio: {precio}\n\nPara continuar:\n1. Escribenos al WhatsApp: https://wa.me/59174222062\n2. Indicanos que quieres {nombre}\n3. Te enviamos el QR de pago\n\nTu licencia llega en 5-15 minutos luego del pago!"
        send_message(sender_id, respuesta)
        return

    send_message(sender_id, "No entendi tu mensaje.\n\nEscribe MENU para ver opciones:\n\nA - Ver productos\nB - Como comprar\nC - Hablar con asesor\nD - Garantia\n\nO escribe el NUMERO del producto (1 al 9) para comprarlo directamente")

# ─── WEBHOOK ──────────────────────────────────────────────────────

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]
                if "message" in event and not event["message"].get("is_echo"):
                    message_text = event["message"].get("text", "")
                    if message_text:
                        handle_message(sender_id, message_text)
    return jsonify({"status": "ok"}), 200

@app.route("/")
def index():
    return "LicenciasBot activo!", 200

# ─── INICIO ───────────────────────────────────────────────────────

scheduler = BackgroundScheduler(timezone="America/La_Paz")
scheduler.add_job(publicar_post_diario, "cron", hour=19, minute=0)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
