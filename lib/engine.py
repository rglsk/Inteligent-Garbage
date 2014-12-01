import pygame
import Queue
import threading

from lib.decision_tree import decision_tree_search
from lib.frames import TrashType, Move, make_game_state_class
from lib.map_generator import generate_map
from lib.random_path import random_path
from lib.state_space_search import state_space_search
from lib.settings import OBSTACLE_FACTOR, RES_X, RES_Y
from lib.settings import MAP_WIDTH, MAP_HEIGHT, colors, TILE_SIZE, Images
from lib.settings import ENTITY_SIZE, trash_image, STEP, TRUNK_CAPACITY
from lib.settings import TEXT_COLOR, ENTITY_FACTOR
from lib.state_space_search import state_space_search, simple_astar
from lib.utils import lerp, go

class Engine:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((RES_X, RES_Y))
        self.font = pygame.font.Font(None, 30)
        (self.map, self.landfill_pos) = generate_map(
            MAP_WIDTH,
            MAP_HEIGHT,
            OBSTACLE_FACTOR
        )
        self.truck_tile_progress = 0 # [0.0..1.0]
        self.GameState = make_game_state_class(ENTITY_FACTOR, TRUNK_CAPACITY)
        self.game_state = self.GameState(self.map)
        self.move_truck = lerp(
            self.game_state.truck_pos,
            self.game_state.truck_pos
        )
        self.move_queue = Queue.Queue(10)
        self.worker_stop = threading.Event()

        def worker_thread():
            for move in decision_tree_search(
                    self.map,
                    self.game_state,
                    self.landfill_pos
                ):
                if self.worker_stop.is_set():
                    break
                self.move_queue.put(move)

        self.worker = threading.Thread(target=worker_thread)
        self.worker.daemon = True
        self.worker.start()

        self.to_landfill = simple_astar(self.map)(self.landfill_pos)

    def get_move(self):
        """fetch move from the queue"""
        move = 0
        try:
            move = self.move_queue.get_nowait()
        except Queue.Empty:
            move = Move.noop
        return move

    def game_loop(self):
        while True:

            # end game if esc key was pressed
            pressed = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or pressed[pygame.K_ESCAPE]:
                    pygame.quit()
                    self.worker_stop.set()
                    self.get_move()
                    return

            # draw tiles
            for row in xrange(MAP_HEIGHT):
                for column in xrange(MAP_WIDTH):
                    pygame.draw.rect(
                        self.display_surface,
                        colors[self.map[row][column]], (
                            column * TILE_SIZE,
                            row * TILE_SIZE,
                            TILE_SIZE,
                            TILE_SIZE
                        )
                    )

            # draw landfill
            self.__draw_image(Images.landfill, self.landfill_pos, ENTITY_SIZE)

            # draw garbage
            for trash_pos in self.game_state.entities:
                self.__draw_image(
                    trash_image[
                        self.game_state.entities[trash_pos].trash_type
                    ],
                    trash_pos,
                    ENTITY_SIZE)

            # animate truck movement
            if self.truck_tile_progress >= 1.0:
                mv = self.get_move()
                self.truck_tile_progress = 0.0
                self.move_truck = lerp(
                    self.game_state.truck_pos,
                    go[mv](self.game_state.truck_pos)
                )
                self.game_state = self.game_state.move(self.map, mv)
                if mv != Move.noop:
                    self.move_queue.task_done()
            else:
                self.truck_tile_progress = self.truck_tile_progress + STEP

            # draw truck
            self.__draw_image(
                Images.truck,
                self.move_truck(self.truck_tile_progress),
                ENTITY_SIZE
            )

            # draw trunk
            text = self.font.render(
                'metal: {}/{}, paper: {}/{}, plastic: {}/{}'.format(
                    self.game_state.trunk[TrashType.metal],
                    TRUNK_CAPACITY,
                    self.game_state.trunk[TrashType.paper],
                    TRUNK_CAPACITY,
                    self.game_state.trunk[TrashType.plastic],
                    TRUNK_CAPACITY
                ), 1, TEXT_COLOR
            )
            self.display_surface.blit(text, (5, 5))

            pygame.display.flip()

    def __draw_image(self, image, pos, image_size):
        self.display_surface.blit(
            image, pygame.Rect(
                int(pos[0] * TILE_SIZE + (TILE_SIZE - image_size) / 2),
                int(pos[1] * TILE_SIZE + (TILE_SIZE - image_size) / 2),
                image_size,
                image_size
            )
        )

if __name__ == "__main__":
    Engine().game_loop()

