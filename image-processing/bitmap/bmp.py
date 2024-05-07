class RGBColor:
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return f"RGB({self.r}, {self.g}, {self.b})"


class BMPFileHeader:
    def __init__(self, fin):
        fin.seek(0)
        self.type = fin.read(2)
        self.size = int.from_bytes(fin.read(4), byteorder="little")
        self.reserved1 = int.from_bytes(fin.read(2), byteorder="little")
        self.reserved2 = int.from_bytes(fin.read(2), byteorder="little")
        self.off_bits = int.from_bytes(fin.read(4), byteorder="little")

    def __str__(self):
        return f"type: {self.type}\nsize: {self.size}\nreserved1: {self.reserved1}\nreserved2: {self.reserved2}\noff_bits: {self.off_bits}"

    def write(self, fout):
        fout.seek(0)
        fout.write(self.type)
        fout.write(self.size.to_bytes(4, byteorder="little"))
        fout.write(self.reserved1.to_bytes(2, byteorder="little"))
        fout.write(self.reserved2.to_bytes(2, byteorder="little"))
        fout.write(self.off_bits.to_bytes(4, byteorder="little"))


class BMPFileDIB:
    def __init__(self, fin):
        fin.seek(14)
        self.size = int.from_bytes(fin.read(4), byteorder="little")
        self.width = int.from_bytes(fin.read(4), byteorder="little")
        self.height = int.from_bytes(fin.read(4), byteorder="little")
        self.planes = int.from_bytes(fin.read(2), byteorder="little")
        self.bit_count = int.from_bytes(fin.read(2), byteorder="little")
        self.compression = int.from_bytes(fin.read(4), byteorder="little")
        self.size_image = int.from_bytes(fin.read(4), byteorder="little")
        self.x_pels_per_meter = int.from_bytes(fin.read(4), byteorder="little")
        self.y_pels_per_meter = int.from_bytes(fin.read(4), byteorder="little")
        self.clr_used = int.from_bytes(fin.read(4), byteorder="little")
        self.clr_important = int.from_bytes(fin.read(4), byteorder="little")

    def __str__(self):
        return f"size: {self.size}\nwidth: {self.width}\nheight: {self.height}\nplanes: {self.planes}\nbit_count: {self.bit_count}\ncompression: {self.compression}\nsize_image: {self.size_image}\nx_pels_per_meter: {self.x_pels_per_meter}\ny_pels_per_meter: {self.y_pels_per_meter}\nclr_used: {self.clr_used}\nclr_important: {self.clr_important}"

    def write(self, fout):
        fout.seek(14)
        fout.write(self.size.to_bytes(4, byteorder="little"))
        fout.write(self.width.to_bytes(4, byteorder="little"))
        fout.write(self.height.to_bytes(4, byteorder="little"))
        fout.write(self.planes.to_bytes(2, byteorder="little"))
        fout.write(self.bit_count.to_bytes(2, byteorder="little"))
        fout.write(self.compression.to_bytes(4, byteorder="little"))
        fout.write(self.size_image.to_bytes(4, byteorder="little"))
        fout.write(self.x_pels_per_meter.to_bytes(4, byteorder="little"))
        fout.write(self.y_pels_per_meter.to_bytes(4, byteorder="little"))
        fout.write(self.clr_used.to_bytes(4, byteorder="little"))
        fout.write(self.clr_important.to_bytes(4, byteorder="little"))


class BMPFilePixelArray:
    def __init__(self, fin, width, height):
        fin.seek(54)

        self.width = width
        self.height = height
        self.padding = (4 - (self.width * 3) % 4) % 4
        self.pixels = []

        for _ in range(self.height):
            row = []
            for __ in range(self.width):
                rgb = RGBColor()
                rgb.b = int.from_bytes(fin.read(1), byteorder="little")
                rgb.g = int.from_bytes(fin.read(1), byteorder="little")
                rgb.r = int.from_bytes(fin.read(1), byteorder="little")
                row.append(rgb)

            fin.read(self.padding)
            self.pixels.insert(0, row)

    def write(self, fout):
        fout.seek(54)
        for i in range(self.height - 1, -1, -1):
            for j in range(self.width):
                fout.write(self.pixels[i][j].b.to_bytes(1, byteorder="little"))
                fout.write(self.pixels[i][j].g.to_bytes(1, byteorder="little"))
                fout.write(self.pixels[i][j].r.to_bytes(1, byteorder="little"))

            for _ in range(self.padding):
                fout.write((0).to_bytes(1, byteorder="little"))

    def print(self):
        for i in range(self.height):
            for j in range(self.width):
                print(self.pixels[i][j], end=", ")
            print()


class BMPFile:
    def __init__(self, file):
        if file is not None:
            self.read(file)

    def is_over24bit(self):
        return self.dib.bit_count >= 24

    def is_bmp(self):
        return self.header.type.decode("utf-8") == "BM"

    def read(self, file):
        if file is None:
            return

        self.header = BMPFileHeader(file)
        self.dib = BMPFileDIB(file)
        self.pixel_array = BMPFilePixelArray(file, self.dib.width, self.dib.height)

    def write(self, fout):
        if fout is None:
            return

        self.header.write(fout)
        self.dib.write(fout)
        self.pixel_array.write(fout)

    def average(self):
        for i in range(self.dib.height):
            for j in range(self.dib.width):
                avg = (
                    self.pixel_array.pixels[i][j].r
                    + self.pixel_array.pixels[i][j].g
                    + self.pixel_array.pixels[i][j].b
                ) // 3
                self.pixel_array.pixels[i][j].r = avg
                self.pixel_array.pixels[i][j].g = avg
                self.pixel_array.pixels[i][j].b = avg

        return self

    def invert(self):
        for i in range(self.dib.height):
            for j in range(self.dib.width):
                self.pixel_array.pixels[i][j].r = 255 - self.pixel_array.pixels[i][j].r
                self.pixel_array.pixels[i][j].g = 255 - self.pixel_array.pixels[i][j].g
                self.pixel_array.pixels[i][j].b = 255 - self.pixel_array.pixels[i][j].b

        return self

    def censor(self, level: int = 1):
        level = max(level, 1)

        for i in range(self.dib.height):
            for j in range(self.dib.width):
                self.pixel_array.pixels[i][j] = self.pixel_array.pixels[i - i % level][
                    j - j % level
                ]

        return self
