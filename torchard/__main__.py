def main() -> None:
    from torchard.core.db import init_db
    from torchard.core.manager import Manager
    from torchard.tui.app import TorchardApp

    conn = init_db()
    manager = Manager(conn)
    TorchardApp(manager).run()


if __name__ == "__main__":
    main()
