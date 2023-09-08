import multiprocessing


class TestObj:
    def __init__(self, value):
        self.value = value


def read_data(conn):
    # Receive the custom object from the Pipe
    custom_obj = conn.recv()

    print("Script2 received:", custom_obj.value)


if __name__ == "__main__":
    parent_conn, child_conn = multiprocessing.Pipe()

    p = multiprocessing.Process(target=read_data, args=(parent_conn,))
    p.start()

    try:
        p.join()  # Keep script2 running until explicitly terminated
    except KeyboardInterrupt:
        print("Script2 has been terminated.")
