from application import create_app


def main():
    app = create_app()
    app.run(debug=app.config['DEBUG'])


if __name__ == '__main__':
    main()
