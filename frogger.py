import pygame, sys


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, type):
        super().__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.velocity = 5
        self.width = 256

        if type == "car":
            self.image = pygame.image.load("sprites/car.png")
            self.image = pygame.transform.scale(self.image, (120, 120))
            self.rect = self.image.get_rect()
        elif type == "water":
            self.image = pygame.image.load("sprites/boat.png")
            self.image = pygame.transform.scale(self.image, (120, 120))
            self.rect = self.image.get_rect()
        self.rect.center = [self.pos_x, self.pos_y]

    def update(self):
        # Updating the position based on the set velocity
        self.pos_x += self.velocity

        # Checking to see when it hits the edge of the screen, then restarting on other side
        if self.velocity > 0 and self.pos_x > 1280 + 64:
            self.pos_x = -self.width
        elif self.velocity < 0 and self.pos_x < -self.width:
            self.pos_x = 1280

        self.rect.center = [self.pos_x, self.pos_y]

        screen.blit(self.image, (self.pos_x, self.pos_y))


class Lane(pygame.sprite.Sprite):
    def __init__(self, pos, type="safe", obsCnt=0):
        super().__init__()
        self.pos_x = 0
        self.pos_y = pos * 128
        self.width = 1280
        self.height = 128
        self.type = type
        self.obsCnt = obsCnt
        self.obstacles = []

        if self.obsCnt > 0:
            for i in range(obsCnt):
                self.obstacles.append(Obstacle(pos * 128, (pos * 128), self.type))

        if self.type == "car":
            self.color = (148, 153, 149)
        elif self.type == "water":
            self.color = (0, 154, 219)
        elif self.type == "safe":
            self.color = (0, 145, 7)
        elif self.type == "finish":
            self.color = (212, 192, 11)

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.pos_x, self.pos_y]

    """
        Obstacle Position Updating
            - This function is responsible for updating the position of the obstacles as they move
    """

    def update(self):
        for obstacle in self.obstacles:
            obstacle.update()

    """
        Obstacle Drawing
            - This function is responsible for drawing the obstacles in the lane
            - Calls each Obstacle's draw() method in order to do this task
    """

    def draw(self, screen):
        for obstacle in self.obstacles:
            obstacle.draw(self.image)

    """
        Collision Checker
            - This function is responsible for detecting when the frog collides with an obstacle,
            as well as when the frog ends up in the finish lane
            - This function resets the frog to the initial position when it collides with an obstacle
    """

    def check(self, frog):
        finish_flag = False
        attach_flag = False
        frog.attach(None)

        # Checking to see if the frog is in the finish lane
        if self.type == "finish":
            frog.reset()
            finish_flag = True

        # Getting the frog's rect boundary object
        rect1 = frog.rect

        # Collision Detection
        for obstacle in self.obstacles:
            # Checking for collision between frog and obstacles
            if rect1.colliderect(obstacle.rect):
                # If we collide with a car, we reset the frog to the start
                if self.type == "car":
                    frog.reset()
                # If we collide with a boat, attach the frog to the boat
                if self.type == "water":
                    attach_flag = True
                    frog.attach(obstacle)
            # If do not collide with the boat, and end up in a water lane, reset the frog to the start
            if not attach_flag and self.type == "water":
                frog.reset()

        # Return the result of the collision check
        return finish_flag


class Frog(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.pos_x_init = pos_x
        self.pos_y_init = pos_y
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.attached = None

        self.image = pygame.image.load("sprites/frog.gif")
        self.rect = self.image.get_rect()
        self.rect.center = [self.pos_x, self.pos_y]

    def move(self, delta_x, delta_y):
        self.pos_x += delta_x * 128
        self.pos_y += delta_y * 128
        self.rect.center = [self.pos_x, self.pos_y]

    def attach(self, obstacle):
        self.attached = obstacle

    def reset(self):
        self.pos_x = self.pos_x_init
        self.pos_y = self.pos_y_init
        self.attach(None)

    def update(self):
        if self.attached:
            self.pos_x += self.attached.velocity

        if self.pos_x + 16 > 1280:
            self.pos_x = 1280 - 16

        if self.pos_x < 0:
            self.pos_x = 0

        if self.pos_y + 16 > 720:
            self.pos_y = 720 - 16

        if self.pos_y < 0:
            self.pos_y = 32

        self.rect.center = [self.pos_x, self.pos_y]
        screen.blit(self.image, (self.pos_x, self.pos_y))


pygame.init()
pygame.key.set_repeat(0, 0)
clock = pygame.time.Clock()

# Creating the Game Screen
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))

# Creating Lanes
lane1 = Lane(0)
lane2 = Lane(1, "water", 1)
lane3 = Lane(2, "car", 1)
lane4 = Lane(3, "finish", 0)
lane_group = pygame.sprite.Group()
lane_group.add(lane1)
lane_group.add(lane2)
lane_group.add(lane3)
lane_group.add(lane4)

# Creating a frog, in the middle center of the safe row
frog = Frog(640, 56)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            frog.move(-1, 0)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            frog.move(1, 0)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            frog.move(0, -1)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            frog.move(0, 1)

    pygame.display.flip()

    # Drawing and updating the group that holds the lane sprites
    lane_group.draw(screen)
    lane_group.update()

    # Updating the frog's position
    frog.update()

    lane = int((frog.pos_y - 56) / 128)
    lane_list = lane_group.sprites()

    collision = lane_list[lane].check(frog)
    if collision:
        frog.reset()

    # for lane in lane_group:
    #     collision = lane.check(frog)
    #     if collision:
    #         frog.reset()

    # frog.update()

    clock.tick(30)
