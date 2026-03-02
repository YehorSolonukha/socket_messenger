class UI():
    def display(self, message: str):
        print(message)
        return

    def read(self) -> str:
        message = input()
        return message