from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import io
from payslip_parser import parse_excel
from database import init_db, migrate_from_json, get_all_employees

# Load environment variables from .env file (if present)
load_dotenv()

app = Flask(__name__)

# --- Configuration from environment ---
FLASK_ENV = os.getenv('FLASK_ENV', 'production')
PORT = int(os.getenv('PORT', 5000))
CORS_ORIGIN = os.getenv('CORS_ORIGIN', '*')  # Restrict in production!
MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE_MB', 10)) * 1024 * 1024  # default 10 MB

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Enable CORS — restrict to your frontend URL in production
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGIN}})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Process an uploaded Excel attendance file and return payslip data."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({"error": "Invalid file type. Please upload an Excel file (.xlsx or .xls)"}), 400

    try:
        # Read file stream into bytes
        file_stream = io.BytesIO(file.read())

        # Pass the stream to the parser
        payslip_data = parse_excel(file_stream)

        return jsonify({
            "message": "File processed successfully",
            "data": payslip_data
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500


@app.route('/api/employees', methods=['GET'])
def list_employees():
    """Return all employees in the database (for admin/debug)."""
    try:
        employees = get_all_employees()
        return jsonify({"employees": employees}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint for deployment platforms."""
    return jsonify({"status": "ok"}), 200


# --- Startup ---
def startup():
    """Initialize database and run one-time migration if needed."""
    init_db()

    # Migrate JSON data to SQLite on first run (safe to re-run)
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'employee_master.json')
    if os.path.exists(json_path):
        migrate_from_json(json_path)
        print("Migration complete. You can now safely delete employee_master.json.")


if __name__ == '__main__':
    startup()
    is_debug = FLASK_ENV != 'production'
    print(f"Starting server on port {PORT} (env={FLASK_ENV}, debug={is_debug})...")
    app.run(debug=is_debug, host='0.0.0.0', port=PORT)
