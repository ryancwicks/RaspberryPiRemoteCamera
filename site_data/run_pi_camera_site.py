import remote_camera

app = remote_camera.create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
