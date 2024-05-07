import sys, getopt

from bmp import *
from utils import *


class BMPApp:
    in_dir = None
    out_dir = None
    methods = []
    bmp = None

    def __init__(self):
        self.bmp = BMPFile(None)

    def __setattr__(self, name: str, value) -> None:
        if name == "methods" and not isinstance(value, Method):
            raise ValueError("Methods must be a list of Method objects")

        super().__setattr__(name, value)

    def process(self):
        print("Processing...")
        for method in self.methods:
            self.bmp = method(self.bmp)
            print(f"`{method.name}` applied")

    def save(self):
        method_chain = (
            ("." + ".".join([method.name for method in self.methods]))
            if len(self.methods) > 0
            else ""
        )
        file = (
            self.out_dir if self.out_dir is not None else f"{self.in_dir}{method_chain}"
        )

        with FileHandler(file, "wb") as fout:
            self.bmp.write(fout)


ARGVS, OPTS = (
    sys.argv[1:],
    dict(short="hmio:", long=["help", "methods=", "in=", "out="]),
)

bmp_app = BMPApp()


try:
    ARGS, values = getopt.getopt(ARGVS, OPTS["short"], OPTS["long"])

    for cur_arg, cur_val in ARGS:
        if cur_arg in ("-h", "--help"):
            show_help()
        elif cur_arg in ("-m", "--methods"):
            for method in cur_val.split(","):
                name, *f_args = method.split(":")

                try:
                    new_method = Method(name, getattr(bmp_app.bmp, name))

                    if len(f_args) > 0:
                        try:
                            new_method.set_args(*[int(arg) for arg in f_args])
                        except ValueError:
                            raise getopt.error(
                                "Arguments of functions must be integers"
                            )

                    bmp_app.methods.append(new_method)
                except AttributeError:
                    raise getopt.error(f"Method {name} is not defined")
        elif cur_arg in ("-i", "--in"):
            bmp_app.in_dir = cur_val
        elif cur_arg in ("-o", "--out"):
            bmp_app.out_dir = cur_val

    if bmp_app.in_dir is None:
        raise getopt.error("Input file is required")

    with FileHandler(bmp_app.in_dir, "rb") as fin:
        bmp_app.bmp.read(fin)
        bmp_app.process()
        bmp_app.save()
except getopt.error as err:
    print(str(err))
else:
    print("All things done!")
finally:
    pass
