def show_help():
    print(
        """Usage
    -h or --help: Display help
    -i or --in: (required) File from `./imgs` to process (Ex: -i lena for ./imgs/lena.bmp)
    -o or --out: (optional) File to save processed image (default: ./imgs/out.bmp)
    -m or --methods: (optional) Apply image processing methods (Ex: -m invert,average,censor)
"""
    )


def open_bmp(file, mode):
    return open("./imgs/" + file + ".bmp", mode)


class Method:
    def __init__(self, name: str, func, *args):
        self.name = name
        self.func = func
        self.args = args

    def __call__(self, *args):
        return self.func(*args if self.args is None else self.args)

    def set_args(self, *args):
        self.args = args


class FileHandler:
    def __init__(self, file, mode):
        self.file = file
        self.mode = mode

    def __enter__(self):
        self.file = open_bmp(self.file, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.close()
