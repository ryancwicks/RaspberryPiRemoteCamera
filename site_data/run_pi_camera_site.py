import remote_camera

if __name__ == "__main__":
    app = remote_camera.create_app()

    app.run(host='0.0.0.0')
