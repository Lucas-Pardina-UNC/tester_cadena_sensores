from app import create_app

app = create_app()  # Create the app instance using the factory

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    #app.run(debug=False, port=5000)
