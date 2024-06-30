import turtle

COLORS = ["red", "purple", "blue", "green", "orange", "yellow"]

SCREEN = turtle.Screen()
SCREEN.title("Demonstrate anything")
SCREEN.setup(width=800, height=600)

t = turtle.Turtle()
t.speed(0)


def spriral_helix(depth=120):
    t.width(2)
    for x in range(depth):
        t.pencolor(COLORS[x % len(COLORS)])
        # t.width(x // 100 + 1)
        t.forward(x)
        t.left(59.5)


def circles(density=50):
    for i in range(density):
        t.circle(2 * i)
        t.circle(-2 * i)
        t.left(i)


def draw_star(length=100):
    for _ in range(5):
        t.forward(length)
        t.right(144)


def sqrfunc(size):
    for _ in range(4):
        t.fd(size)
        t.left(90)
        size = size + 5


# t.color("red")
# draw_star()

# t.color("blue")
# for i in range(4):
#     sqrfunc(6 + i * 20)

# circles()

spriral_helix()

turtle.done()

input("Press ENTER key to exit...")
