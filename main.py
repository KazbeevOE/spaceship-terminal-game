import asyncio
import curses
import time
import random
import os

from itertools import cycle

from fire_animation import fire
from curses_tools import draw_frame, read_controls, get_frame_size
from frames_loader import load_frames_from_dir, load_frame_from_file
from physics import update_speed
from space_garbage import animate_flying_garbage, obstacles


TIC_TIMEOUT = 0.1
STAR_SHAPES = '+*.:'
FRAMES_PATH = 'frames'
ROCKET_FRAMES_PATH = os.path.join(FRAMES_PATH, 'rocket_frames')
GARBAGE_FRAMES_PATH = os.path.join(FRAMES_PATH, 'garbage_frames')
GAME_OVER_FRAME_PATH = os.path.join(FRAMES_PATH, 'game_over_frame', 'game_over.txt')


def draw(canvas):
  border_size = 1
  window_height, window_width = canvas.getmaxyx()
  frames_container = []
  level = [0]

  canvas.nodelay(True)
  curses.curs_set(False)
  canvas.border()

  coroutines = [
    blink(canvas, row, column, symbol, random.randint(0, 3)) for row, column, symbol in generate_star_parametres(canvas, border_size, random.randint(50, 100))
    ]

  spaceship_frames = load_frames_from_dir(ROCKET_FRAMES_PATH)
  spaceship_animation_coroutine = animate_spaceship(frames_container, spaceship_frames)

  spaceship_run_coroutine = run_spaceship(canvas,coroutines, frames_container, border_size)

  garbage_frames = load_frames_from_dir(GARBAGE_FRAMES_PATH)
  fill_orbit_coroutine = fill_orbit_with_garbage(
    canvas, 
    coroutines, 
    border_size, 
    level, 
    garbage_frames
  )

  coroutines.append(spaceship_animation_coroutine)
  coroutines.append(spaceship_run_coroutine)

  coroutines.append(fill_orbit_coroutine)

  screens = (canvas, canvas)
  run_event_loop(screens, coroutines)


async def blink(canvas, row, column, symbol='*', delay=0):
  while True:
    if delay == 0:
      canvas.addstr(row, column, symbol, curses.A_DIM)
      await go_to_sleep(2)
      delay += 1

    if delay == 1:
      canvas.addstr(row, column, symbol)
      await go_to_sleep(0.3)
      delay += 1

    if delay == 2:
      canvas.addstr(row, column, symbol, curses.A_BOLD)
      await go_to_sleep(0.5)
      delay += 1
    
    if delay == 3:
      canvas.addstr(row, column, symbol)
      await go_to_sleep(0.3)
      delay = 0


async def go_to_sleep(tics=1):
  iteration_count = int(tics * 10)

  for _ in range(iteration_count):
    await asyncio.sleep(0)


def generate_star_parametres(canvas, border_size, amount_of_stars=50):
  window_height, window_width = canvas.getmaxyx()
  
  for star in range(amount_of_stars):
    row = random.randint(1, window_height - border_size - 1)
    column = random.randint(1, window_width - border_size - 1)
    symbol = random.choice(STAR_SHAPES)
    yield row, column, symbol


async def animate_spaceship(frames_container, frames):
  frames_cycle = cycle(frames)

  while True:
    frames_container.clear()
    frame = next(frames_cycle)
    frames_container.append(frame)
    await asyncio.sleep(0)


async def run_spaceship(canvas, coroutines, frames_container, border_size):
  main_window_height, main_window_width = canvas.getmaxyx()

  start_ship_row = main_window_height - border_size
  start_ship_column = main_window_width / 2

  frame_size_y, frame_size_x = get_frame_size(frames_container[0])

  frame_pos_x = round(start_ship_row) - round(frame_size_x / 2)
  frame_pos_y = round(start_ship_column)

  row_speed, column_speed = 0, 0

  while True:
    direction_y, direction_x, spacepressed = read_controls(canvas)

    if spacepressed:
      shot_pos_x = frame_pos_x + round(frame_size_x / 2)
      shot_pos_y = frame_pos_y
      shot_coroutine = fire(canvas, shot_pos_y, shot_pos_x)
      coroutines.append(shot_coroutine)

    row_speed, column_speed = update_speed(
      row_speed,
      column_speed,
      direction_y,
      direction_x
    )

    frame_pos_x += column_speed
    frame_pos_y += row_speed

    frame_pos_x_max = frame_pos_x + frame_size_x
    frame_pos_y_max = frame_pos_y + frame_size_y

    game_field_x_max= main_window_width - border_size
    game_field_y_max = main_window_height - border_size

    frame_pos_x = min(frame_pos_x_max, game_field_x_max) - frame_size_x
    frame_pos_y = min(frame_pos_y_max, game_field_y_max) - frame_size_y

    frame_pos_x = max(frame_pos_x, border_size)
    frame_pos_y = max(frame_pos_y, border_size)
    frame = frames_container[0]

    draw_frame(canvas, frame_pos_y, frame_pos_x, frame)
    await asyncio.sleep(0)
    draw_frame(canvas, frame_pos_y, frame_pos_x, frame, negative=True)

    gameover_frame = load_frame_from_file(GAME_OVER_FRAME_PATH)
    for obstacle in obstacles:
      if obstacle.has_collision(frame_pos_y, frame_pos_x):
        gameover_coroutine = show_gameover(canvas, gameover_frame) 
        coroutines.append(gameover_coroutine)
        return

async def fill_orbit_with_garbage(canvas, coroutines, border_size, level, garbage_frames, timeout_minimal=0.1):
  _, columns_number = canvas.getmaxyx()
  
  while True:
    garbage_frame = random.choice(garbage_frames)
    _, garbage_frame_size_x = get_frame_size(garbage_frame)
    column = random.randint(
      border_size,
      columns_number - border_size - garbage_frame_size_x)
    
    garbage_coroutine = animate_flying_garbage(canvas, column, garbage_frame)
    coroutines.append(garbage_coroutine)

    garbage_respawn_timeout = calculate_respawn_timeout(level)

    if garbage_respawn_timeout <= timeout_minimal:
      garbage_respawn_timeout = timeout_minimal
    await go_to_sleep(garbage_respawn_timeout)


def calculate_respawn_timeout(level, initial_timeout=5, complexity_factor=5):
    timeout_step = level[0] / complexity_factor
    respawn_timeout = initial_timeout - timeout_step
    return respawn_timeout

async def show_gameover(canvas, gameover_frame):
  window_height, window_width = canvas.getmaxyx()
  go_frame_size_y, go_frame_size_x = get_frame_size(gameover_frame)
  go_message_pos_y = round(window_height / 2) - round(go_frame_size_y)
  go_message_pos_x = round(window_width / 2) - round(go_frame_size_x / 2)

  while True:
    draw_frame(canvas, go_message_pos_y, go_message_pos_x, gameover_frame)
    await asyncio.sleep(0)

def run_event_loop(screens, coroutines):
  while True:
    index = 0

    while index < len(coroutines):
      coroutine = coroutines[index]

      try:
        coroutine.send(None)
      except StopIteration:
        index = coroutines.index(coroutine)
        coroutines.remove(coroutine)
      else:
        index += 1

    for screen in screens:
      screen.refresh()
    time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)