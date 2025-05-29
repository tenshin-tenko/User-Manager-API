from app.server.app import app

def main():
    from uvicorn import run
    run(app, host='127.0.0.1', port=8080)

if __name__ == "__main__":
    main()