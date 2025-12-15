from flask import Flask, request, jsonify
from urllib.parse import urlparse
from db import scans_collection
from scanner import static_scan, dynamic_scan

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "URL is required"}), 400

    url = data["url"].strip()

    if not url.startswith("http"):
        url = "https://" + url

    try:
        static_results = static_scan(url)
        dynamic_results = dynamic_scan(url)

        scan_doc = {
            "url": url,
            "static": static_results,
            "dynamic": dynamic_results,
            "status": "completed"
        }

        inserted = scans_collection.insert_one(scan_doc)

        return jsonify({
            "scan_id": str(inserted.inserted_id),
            "summary": {
                "scripts": len(static_results["scripts"]),
                "styles": len(static_results["styles"]),
                "images": len(static_results["images"]),
                "iframes": len(static_results["iframes"]),
                "inline_scripts": static_results["inline_scripts"]
            }
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
