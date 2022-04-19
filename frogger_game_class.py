import pygame, sys
import random

"""
    Score Class
        - This class is responsible for keeping track of...
            - The score
            - The level
            - The gameover condition
        - This class is also responsible for drawing the remaining lives, and level on the screen
"""


class Score(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        # self.pos_x = pos_x
        # self.pos_y = pos_y
        self.level = 1
        self.lives = 5
        self.gameover = False

    """
        Draw the HUD
            - This function is responsible for display the number of lives remaining, as well as the current level
    """

    def draw_hud(self, screen):
        font = pygame.font.Font("sprites/Oswald-Regular.ttf", 24)
        text = font.render(f"Lives: {self.lives} Level: {self.level}", True, (0, 0, 0))
        screen.blit(text, (1000, 32))

    """
        Remove life function
            - removes a life from the starting amount whenever a collison occurs
    """

    def remove_life(self):
        self.lives -= 1

        # Triggering the gameover flag once the lives reach 0
        if self.lives <= 0:
            self.gameover = True

    """
        Advance Level Function
            - This function is responsible for advancing the level count on successful completion of a level
    """

    def advance_level(self):
        self.level += 1

    """
        Check for Gameover
            - This function is responsible for checking to see if the game is over or not
            - The game is over when the lives reach 0
    """

    def gameOverCheck(self):
        if self.lives <= 0:
            return True


"""
    Obstacle Class
        - This class is responsible for keeping track of
            - The obstacles' position
            - The obstacles' velocity
            - The obstacles' collision with the character
        - This class is responsible for drawing
            - The obstacles in the lanes
"""


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos_y, type, level):
        super().__init__()
        directionChooser = random.randrange(0, 10)
        self.pos_x = random.randrange(0, 1280)
        self.pos_y = pos_y
        self.pothole_x = self.pos_x
        self.pothole_y = pos_y + 32
        self.level = level
        self.potHoleFlag = random.randrange(0, 10)
        self.type = type

        if self.level % 5 == 0:
            spdMultiplier = self.level / 5 + 1
        else:
            spdMultiplier = 1

        if directionChooser < 5:
            self.velocity = spdMultiplier * (random.randrange(-5, -1))
        elif directionChooser >= 5:
            self.velocity = spdMultiplier * (random.randrange(1, 5))
        self.width = 256

        if type == "car":
            self.image = pygame.image.load("sprites/qline.png")
            self.image = pygame.transform.scale(self.image, (120, 120))
            self.rect = self.image.get_rect()
            self.rect2 = None
            if self.potHoleFlag < 7:
                self.image2 = pygame.image.load("sprites/pothole.png")
                self.rect2 = self.image2.get_rect()
                self.rect2.center = [self.pos_x, self.pos_y]
        elif type == "water":
            self.rect2 = None
            self.image = pygame.image.load("sprites/boat.png")
            self.image = pygame.transform.scale(self.image, (120, 120))
            self.rect = self.image.get_rect()
        self.rect.center = [self.pos_x, self.pos_y]

    """
        Update Obstacles
            - This is the function we call to update the position of an obstacle based on its velocity
            - This function also handles the obstacles running off the screen
    """

    def update(self, screen):
        # Updating the position based on the set velocity
        self.pos_x += self.velocity

        # Checking to see when it hits the edge of the screen, then restarting on other side
        if self.velocity > 0 and self.pos_x > 1280 + 64:
            self.pos_x = -self.width
        elif self.velocity < 0 and self.pos_x < -self.width:
            self.pos_x = 1280

        self.rect.center = [self.pos_x, self.pos_y]

        screen.blit(self.image, (self.pos_x, self.pos_y))

        if self.potHoleFlag < 7 and self.type == "car":
            self.rect2.center = [self.pothole_x, self.pothole_x]
            screen.blit(self.image2, (self.pothole_x, self.pothole_y))


class Lane(pygame.sprite.Sprite):
    def __init__(self, pos, type="safe", obsCnt=0, level=1):
        super().__init__()
        self.pos_x = 0
        self.pos_y = pos * 128
        self.width = 1280
        self.height = 128
        self.type = type
        self.obsCnt = obsCnt
        self.obstacles = []
        self.level = level

        # Check if we need obstacles, because start and finish don't have obstacles
        if self.obsCnt > 0:
            for i in range(obsCnt):
                self.obstacles.append(Obstacle((pos * 128), self.type, self.level))

        # Drawing lane based on type of lane we need

        if self.type == "car":
            self.image = pygame.image.load("sprites/road.png")
            self.rect = self.image.get_rect()
            self.rect.topleft = [self.pos_x, self.pos_y]
        elif self.type == "water":
            self.image = pygame.image.load("sprites/water.png")
            self.rect = self.image.get_rect()
            self.rect.topleft = [self.pos_x, self.pos_y]
        elif self.type == "safe":
            self.image = pygame.image.load("sprites/bedroom.png")
            self.rect = self.image.get_rect()
            self.rect.topleft = [self.pos_x, self.pos_y]

        elif self.type == "finish":
            self.image = pygame.image.load("sprites/gm_background.png")
            self.rect = self.image.get_rect()
            self.rect.topleft = [self.pos_x, self.pos_y]

    """
        Obstacle Position Updating
            - This function is responsible for updating the position of the obstacles as they move
    """

    def update(self, screen):
        for obstacle in self.obstacles:
            obstacle.update(screen)

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
            - This function also deals with the finish condition
    """

    def check(self, frog, score):
        finish_flag = False
        attach_flag = False
        frog.attach(None)

        # Checking to see if the frog is in the finish lane
        if self.type == "finish":
            finish_flag = True

        # Getting the frog's rect boundary object
        rect1 = frog.rect

        # Collision Detection
        for obstacle in self.obstacles:
            # if obstacle.rect2 != None:
            #     if rect1.colliderect(obstacle.rect2):
            #         frog.reset()
            #         score.remove_life()
            # Checking for collision between frog and obstacles
            if rect1.colliderect(obstacle.rect):
                # If we collide with a car, we reset the frog to the start
                if self.type == "car":
                    frog.reset()
                    score.remove_life()
                # If we collide with a boat, attach the frog to the boat
                if self.type == "water":
                    attach_flag = True
                    frog.attach(obstacle)
            # If do not collide with the boat, and end up in a water lane, reset the frog to the start
            elif not attach_flag and self.type == "water":
                frog.reset()
                score.remove_life()

        # Return the result of the collision check
        return finish_flag


"""
    Frog Class
        - This class is responsible for keeping track of...
            - The position of the frog
            - If the frog is attached to a boat
        - This class is responsible for drawing...
            - The character in its current position by calling the update method
"""


class Frog(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.pos_x_init = pos_x
        self.pos_y_init = pos_y
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.attached = None

        self.image = pygame.image.load("sprites/student.png")
        self.rect = self.image.get_rect()
        self.rect.center = [self.pos_x, self.pos_y]

    """
        Move Function
            - This function is responsible for moving the frog
    """

    def move(self, delta_x, delta_y):
        self.pos_x += delta_x * 128
        self.pos_y += delta_y * 128
        self.rect.center = [self.pos_x, self.pos_y]

    """
        Attach Function
            - This function is responsible for attaching the character to a boat obstacle
    """

    def attach(self, obstacle):
        self.attached = obstacle

    """
        Reset Function
            - This function is responsible for resetting the character back to the start
            - This function also dettaches the character from any obstacles
    """

    def reset(self):
        self.pos_x = self.pos_x_init
        self.pos_y = self.pos_y_init
        self.attach(None)

    """
        Update Function
            - This function is responsible for updating the position of the character
            - This function also takes care of when the character tries to run off of the screen
            - This function also takes care of re-drawing the character on the screen
    """

    def update(self, screen, screenHeight):
        if self.attached:
            self.pos_x += self.attached.velocity

        if self.pos_x + 16 > 1280:
            self.pos_x = 1280 - 16

        if self.pos_x < 0:
            self.pos_x = 0

        if self.pos_y + 16 > screenHeight:
            self.pos_y = 720 - 16

        if self.pos_y < 0:
            self.pos_y = 32

        self.rect.center = [self.pos_x, self.pos_y]
        screen.blit(self.image, (self.pos_x, self.pos_y))


class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.lanes = pygame.sprite.Group()
        self.frog = None
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Interview Rush")
        self.score = Score(self.screen)

        pygame.key.set_repeat(0, 0)
        self.frog = Frog(640, 56)

    def makeLanes(self):
        laneCount = self.score.level
        counter = 1

        self.screen.fill((0, 0, 0))
        self.lanes.empty()
        self.lanes.add(Lane(0, "safe"))

        if laneCount <= 8:
            for i in range(0, laneCount):
                laneDecider = random.randrange(0, 10)

                if counter >= 4 and counter < 9:
                    self.screen_height += 64
                    self.screen = pygame.display.set_mode(
                        (self.screen_width, self.screen_height)
                    )
                # Deciding between water and car lane
                if laneDecider < 5:
                    self.lanes.add(Lane(counter, "car", 1, self.score.level))
                elif laneDecider >= 5:
                    self.lanes.add(Lane(counter, "water", 1, self.score.level))

                counter += 1

            self.lanes.add(Lane(counter, "finish"))
        else:
            for i in range(0, 9):
                if counter >= 4 and counter < 9:
                    self.screen_height += 64
                    self.screen = pygame.display.set_mode(
                        (self.screen_width, self.screen_height)
                    )
                self.lanes.add(Lane(counter, "car", 1))
                counter += 1

            self.lanes.add(Lane(counter, "finish"))

    def gameOver(self):
        self.screen.fill((202, 204, 207))

        font = pygame.font.Font("sprites/Oswald-Regular.ttf", 24)
        text = font.render("Game Over!", True, (0, 0, 0))

        restartText = font.render(
            "[R] to restart the game               [E] to exit", True, (0, 0, 0)
        )

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.score = Score(self.screen)
                    self.makeLanes()
                    self.startUp()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    pygame.quit()
                    sys.exit()

            self.screen.blit(text, (500, 32))
            self.screen.blit(restartText, (500, 300))
            pygame.display.flip()
            self.clock.tick(30)

    def intro(self):
        self.screen.fill((202, 204, 207))

        font = pygame.font.Font("sprites/Oswald-Regular.ttf", 24)
        text = font.render("Welcome to Interview Rush!", True, (0, 0, 0))
        text2 = font.render(
            "The goal of this game is to get to as many interviews as possible",
            True,
            (0, 0, 0),
        )
        text3 = font.render(
            "by dodging the Q-Line and hopping on boats to get to the GM Building",
            True,
            (0, 0, 0),
        )
        qlineText = font.render(
            ": Dodge these, when hit you will lose a life", True, (0, 0, 0)
        )
        boatText = font.render(
            ": Ride on these to get across the water", True, (0, 0, 0)
        )

        startText = font.render(
            "[S] to start the game               [E] to exit", True, (0, 0, 0)
        )

        image = pygame.image.load("sprites/qline.png")
        image2 = pygame.image.load("sprites/boat.png")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    self.makeLanes()
                    self.startUp()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    pygame.quit()
                    sys.exit()

            self.screen.blit(text, (500, 32))
            self.screen.blit(text2, (300, 64))
            self.screen.blit(text3, (300, 96))
            self.screen.blit(image, (200, 128))
            self.screen.blit(qlineText, (350, 175))

            self.screen.blit(image2, (200, 250))
            self.screen.blit(boatText, (350, 260))

            self.screen.blit(startText, (500, 300))
            pygame.display.flip()
            self.clock.tick(30)

    def startUp(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    self.frog.move(-1, 0)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    self.frog.move(1, 0)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    self.frog.move(0, -1)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    self.frog.move(0, 1)

            pygame.display.flip()

            # Drawing and updating the group that holds the lane sprites
            self.lanes.draw(self.screen)
            self.lanes.update(self.screen)

            # Updating the frog's position
            self.frog.update(self.screen, self.screen_height)

            lane = int((self.frog.pos_y - 56) / 128)
            lane_list = self.lanes.sprites()

            collision = lane_list[lane].check(self.frog, self.score)

            if self.score.gameOverCheck():
                self.gameOver()

            if collision:
                self.frog.reset()
                self.score.advance_level()
                self.makeLanes()

            if self.score.gameover == True:
                pygame.quit()

            self.score.draw_hud(self.screen)
            self.clock.tick(30)


if __name__ == "__main__":
    game = Game()
    game.intro()
    # game.makeLanes()
    # game.startUp()
