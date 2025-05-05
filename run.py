from app import app

if __name__ == '__main__':
    # Note: For development only. Use a production WSGI server (like Gunicorn) for deployment.
    app.run(debug=True, host='0.0.0.0', port=5000) 