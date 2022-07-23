import time
from turtle import Screen, Turtle
from functools import partial
from random import randint

# constants
up_key, down_key, left_key, right_key, space_key = \
    "Up", "Down", "Left", "Right", "space"
HEADING_BY_KEY = {up_key: 90, down_key: 270, right_key: 0, left_key: 180}
HEADING_BY_ANGLE = {0: 0, 1: 90, 2: 90, 3: 180, 4: 180, 5: 270, 6: 270, 7: 0}
snake_speed = 200
monster_speed = 300

# global variables
g_last_key_pressed = None
g_screen = None
g_snake = None
g_intro = None
g_monster = None
g_paused = False
g_contact_count = 0
g_time = 0
g_snake_length = 6
g_head_size = 20
g_snakesegments = []  # snake's body
g_foodnumbers = {}


def gamescreen(width=500, height=500):
    s = Screen()
    s.title("Snake by Winston")
    s.setup(width, height)
    s.tracer(0)  # Turns off the screen updates
    s.onkeypress(partial(key_pressed, space_key), space_key)
    s.onkeypress(partial(key_pressed, up_key), up_key)
    s.onkeypress(partial(key_pressed, down_key), down_key)
    s.onkeypress(partial(key_pressed, left_key), left_key)
    s.onkeypress(partial(key_pressed, right_key), right_key)
    return s


def create_turtle(shape="square", hidden=None, x=0, y=0, color="Black"):
    t = Turtle(shape)
    t.color(color)
    t.penup()
    if hidden:
        t.hideturtle()
    t.goto(x, y)
    return t


def text_intro():
    text = create_turtle(x=-200, y=120, hidden=True)
    text.write("Welcome to Winston's version of Snake \n\n" +
               "You are going to use the 4 arrow keys to move the snake \n" +
               "around the screen,trying to consume all the food items \n" +
               "before the monster catches you...\n\n" +
               "Click anywhere to start the game.",
               font="arial 10 bold")
    return text


def create_snakehead():
    return create_turtle(color="red")


def create_monster():
    while True:
        x, y = randint(-230, 230), randint(-230, 230)
        if abs(x) >= 100 and abs(y) >= 100:
            break
    return create_turtle(color="purple", x=x, y=y)

# snake food generator


def spawn_numbers():
    for i in range(1, 10):
        x, y = randint(-230, 230), randint(-230, 230)
        turtle = create_turtle(x=x, y=y, hidden=True)
        turtle.write(str(i), False, "center")
        g_foodnumbers[turtle.pos()] = i


def key_pressed(key):
    global g_last_key_pressed, g_paused
    if key == space_key:
        g_paused = not g_paused
    else:
        g_last_key_pressed = key
        print('key_pressed', key)


def is_move_valid(move):
    x, y = g_snake.pos()
    bound = 230
    print("is_move_valid()", x, y, bound)
    if move == up_key:
        return y < bound
    elif move == down_key:
        return y > -bound
    elif move == right_key:
        return x < bound
    elif move == left_key:
        return x > -bound


def collision(t1, t2):  # collision between turtles or snake with food
    global g_head_size
    if type(t1) is Turtle:
        dist = t1.distance(t2)
        return dist <= g_head_size
    return False


def move_snake(move):
    if g_paused or g_last_key_pressed is None or is_move_valid(move) is False:
        return

    # Head now becomes the body
    g_snake.color("blue", "black")  # head changes colour
    g_snake.stamp()
    g_snakesegments.insert(0, g_snake.position())

    # set the forward direction {E,W,S,N} according to  the key pressed
    g_snake.setheading(HEADING_BY_KEY[move])
    g_snake.forward(g_head_size)
    g_snake.color("red")

    # moving the snake's tail
    if len(g_snake.stampItems) >= g_snake_length:
        g_snake.clearstamps(1)
        g_snakesegments.pop()  # removes lastbody position from list
    g_screen.update()


def update_snake():

    global g_snake_length, g_contact_count

    if collision(g_snake, g_monster):
        return

    print("update_snake", len(g_foodnumbers.keys()))  # number of food left

    move_snake(g_last_key_pressed)

    # checks if snake collides with any numbers
    for number in g_screen.turtles():
        pos = number.position()
        if pos in g_foodnumbers:
            if collision(g_snake, number):
                number.clear()  # clear the text string
                g_snake_length += g_foodnumbers[pos]
                g_foodnumbers.pop(pos)
                break

    # g_screen.update()
    update_game_status("snake")


# monster chasing after the snake
def update_monster():

    # based on value of angle (monster towards snake's head)
    # to determine which direction to move the monster
    # 0 - east, 90 - north, 180 - west, 270 - south
    # tells the monster the required direction to chase the snake
    angle = g_monster.towards(g_snake)

    # decide the direction towards snake's head
    quadrant = int(angle/45)
    heading = HEADING_BY_ANGLE[quadrant]

    g_monster.setheading(heading)
    g_monster.forward(g_head_size)

    count_body_contact_with_snake(g_monster)

    update_game_status()


def update_game_status(type="monster"):

    # Update the status
    title = "Snake: Contacted: {}, Time: {}".format(
        g_contact_count, int(time.time() - g_time_started))
    g_screen.title(title)
    g_screen.update()

    if collision(g_snake, g_monster):
        g_snake.write("Game Over!", False, "center",
                      ("Comic Sans", 14, "bold"))
        return

    if is_winner():
        g_snake.write("Winner!", False, "center", ("Comic Sans", 25, "bold"))
        return

    if type == "snake":
        speed = snake_speed * \
            2 if len(g_snake.stampItems) < g_snake_length-1 else snake_speed
        g_screen.ontimer(update_snake, speed)
    else:
        g_screen.ontimer(update_monster, randint(
            monster_speed, monster_speed+100))


def count_body_contact_with_snake(monster):
    global g_contact_count
    for body in g_snakesegments:
        if collision(monster, body):
            g_contact_count += 1
            print("Monster has made contact with the snake's body!")
            break


def is_winner():
    return len(g_snake.stampItems) == (g_snake_length-1) and \
        len(g_foodnumbers.keys()) == 0


def start_game(x, y):
    global g_time_started
    g_intro.clear()
    spawn_numbers()
    g_time_started = time.time()
    g_screen.ontimer(update_snake, snake_speed)
    g_screen.ontimer(update_monster, monster_speed)
    g_screen.onscreenclick(None)


if __name__ == "__main__":
    g_screen = gamescreen()
    g_snake = create_snakehead()
    g_monster = create_monster()
    g_intro = text_intro()
    g_screen.update()
    g_screen.onscreenclick(start_game)
    g_screen.listen()
    g_screen.mainloop()
