from server.app import app,game_main_thread


if __name__ == "__main__":
    game_main_thread.start()
    app.run(debug=True, port=5000,host="0.0.0.0")