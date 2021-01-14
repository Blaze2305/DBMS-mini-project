from app import app as application
from flask_cors import CORS

CORS(application)

if __name__ == "__main__":
	application.run(host="0.0.0.0",debug=True)