"""
FRechnung Flask REST-API (Cloud/Stateless Version)

Design:
  - Server ist vollstaendig stateless
  - Firmendaten kommen bei jedem Request vom Client (sessionStorage)
  - Logos als Base64 im Request, nie gespeichert
  - Kein Keyring, keine Dateien, kein OS-Zustand
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import base64
import os
import sys
import io
import tempfile

from config_manager import ConfigManager
from pdf_generator import create_invoice_pdf, THEME_NAMES


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


FRONTEND_DIR = resource_path("frontend")
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)
config_manager = ConfigManager()


@app.route("/")
def index():
    # Datei direkt ausliefern — kein manuelles Lesen noetig
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(FRONTEND_DIR, "favicon.ico", mimetype="image/x-icon")


@app.route("/api/provider", methods=["GET"])
def get_provider():
    return jsonify(config_manager.get_service_provider())


@app.route("/api/provider", methods=["POST"])
def save_provider():
    # No-op: Client speichert in sessionStorage
    return jsonify({"ok": True})


@app.route("/api/provider/logo/upload", methods=["POST"])
def upload_logo():
    """Validiert Logo-Base64 und gibt es zurueck. Kein Speichern am Server."""
    data = request.get_json()
    b64  = data.get("data", "")
    name = data.get("name", "logo.png")

    if not b64:
        return jsonify({"ok": False, "error": "Keine Bilddaten empfangen."}), 400

    try:
        raw = base64.b64decode(b64)
        if len(raw) > 5 * 1024 * 1024:
            return jsonify({"ok": False, "error": "Logo zu gross (max. 5 MB)."}), 400
        return jsonify({"ok": True, "logo_b64": b64, "name": name})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/themes", methods=["GET"])
def get_themes():
    return jsonify(THEME_NAMES)


@app.route("/api/generate-pdf", methods=["POST"])
def generate_pdf():
    """
    Vollstaendig stateless: Alle Daten inkl. Firmendaten und Logo als Base64
    kommen im Request. Server speichert nichts.
    """
    payload   = request.get_json()
    inv_data  = payload.get("invoice",  {})
    recv_data = payload.get("receiver", {})
    items     = payload.get("items",    [])
    company   = payload.get("company",  {})
    theme     = payload.get("theme",    THEME_NAMES[0])
    logo_b64  = payload.get("logo_b64", "")

    if not items:
        return jsonify({"ok": False, "error": "Keine Artikel uebergeben."}), 400
    if not company.get("company_name"):
        return jsonify({"ok": False, "error": "Firmenname fehlt."}), 400

    logo_path = ""
    tmp_logo  = None
    if logo_b64:
        try:
            logo_bytes = base64.b64decode(logo_b64)
            # 'wb' (binary write) — nicht 'w', da Bilddaten keine Texte sind
            tmp_logo = tempfile.NamedTemporaryFile(
                delete=False, suffix=".png", prefix="logo_tmp_", mode="wb"
            )
            tmp_logo.write(logo_bytes)
            tmp_logo.close()
            logo_path = tmp_logo.name
        except Exception:
            logo_path = ""

    try:
        result    = create_invoice_pdf(
            inv_data, recv_data, items, company,
            logo_path=logo_path,
            theme_name=theme,
        )
        pdf_bytes = result[0] if isinstance(result, tuple) else result
        b64_out   = base64.b64encode(pdf_bytes).decode("utf-8")
        return jsonify({"ok": True, "pdf_base64": b64_out})
    except Exception as e:
        import traceback
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()}), 500
    finally:
        if tmp_logo and os.path.exists(tmp_logo.name):
            try:
                os.unlink(tmp_logo.name)
            except Exception:
                pass


@app.route("/api/save-pdf", methods=["POST"])
def save_pdf():
    payload  = request.get_json()
    b64      = payload.get("pdf_base64", "")
    filename = payload.get("filename", "Rechnung.pdf")
    try:
        pdf_bytes = base64.b64decode(b64)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)