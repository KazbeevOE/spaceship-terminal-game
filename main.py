import asyncio
import curses
import time
import random
import os

from itertools import cycle

from fire_animation import fire
from curses_tools import draw_frame, read_controls, get_frame_size
from frames_loader import load_frames_from_dir


TIC_TIMEOUT = 0.1
STAR_SHAPES = '+*.:'
FRAMES_PATH = 'frames'
ROCKET_FRAMES_PATH = os.path.join(FRAMES_PATH, 'rocket_frames')

def draw(canvas):
  border_size = 1
  window_heigh, window_width = canvas.getmaxyx()
  mid_row = round(window_heigh - border_size)
  mid_column = round(window_width / 2)

  frames_container = []

  canvas.border()
  canvas.nodelay(True)
  curses.curs_set(False)

  coroutines = [
    blink(canvas, row, column, symbol, random.randint(0, 3)) for row, column, symbol in generate_star_parametres(canvas, border_size, random.randint(50, 100))
    ]

  spaceship_frames = load_frames_from_dir(ROCKET_FRAMES_PATH)

  spaceship_animation_coroutine = animate_spaceship(frames_container, spaceship_frames)

  spaceship_run_coroutine = run_spaceship(canvas, frames_container, border_size)

  shot_coroutine = fire(canvas, mid_row, mid_column)

  coroutines.append(spaceship_animation_coroutine)
  coroutines.append(spaceship_run_coroutine)
  
  coroutines.append(shot_coroutine)

  while True:
    for coroutine in coroutines:
      try:
        coroutine.send(None)
      except StopIteration:
        coroutines.remove(coroutine)

    time.sleep(0.1)
    canvas.refresh()


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


async def go_to_sleep(tics):
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


async def run_spaceship(canvas, frames_container, border_size):
  main_window_height, main_window_width = canvas.getmaxyx()

  start_ship_row = main_window_height - border_size
  start_ship_column = main_window_width / 2

  frame_size_y, frame_size_x = get_frame_size(frames_container[0])

  frame_pos_x = round(start_ship_row) - round(frame_size_x / 2)
  frame_pos_y = round(start_ship_column)

  while True:
    direction_y, direction_x, spacepressed = read_controls(canvas)

    frame_pos_x += direction_x
    frame_pos_y += direction_y

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

 
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)