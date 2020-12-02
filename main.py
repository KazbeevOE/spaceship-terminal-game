import asyncio
import curses
import time
import random
import os

from itertools import cycle

from fire_animation import fire
from curses_tools import draw_frame


TIC_TIMEOUT = 0.1
STAR_SHAPES = '+*.:'
FRAMES_PATH = 'frames'
ROCKET_FRAMES_PATH = os.path.join(FRAMES_PATH, 'rocket_frames')

def draw(canvas):
  main_window_height, main_window_width = canvas.getmaxyx()
  border_size = 1
  mid_row = main_window_height // 2
  mid_column = main_window_width // 2
  max_amount_of_stars = random.randint(50, 100)

  canvas.border()
  curses.curs_set(False)
  canvas.refresh()

  coroutines = []
  spaceship_frames = []

  for file_number in range(1, 3):
    with open(ROCKET_FRAMES_PATH + f'/rocket_frame_{file_number}.txt', 'r') as rf:
      rocket_frame = rf.read()
    spaceship_frames.append(rocket_frame)
  
  spaceship_coroutine = animate_spaceship(canvas, mid_row, mid_column, spaceship_frames)
  coroutines.append(spaceship_coroutine)

  shot_coroutine = fire(canvas, mid_row, mid_column)
  coroutines.append(shot_coroutine)

  for s in range(max_amount_of_stars):
    row, column, symbol = generate_star_parametres(main_window_height, main_window_width, border_size)
    delay = random.randint(0, 3)
    coroutine = blink(canvas, row, column, symbol, delay)
    coroutines.append(coroutine)

  while True:
    for coroutine in coroutines:
      try:
        coroutine.send(None)
      except StopIteration:
        coroutines.remove(coroutine)

    time.sleep(0.1)
    canvas.refresh()

async def animate_spaceship(canvas, row, column, spaceship_frames):
  frames_cycle = cycle(spaceship_frames)

  while True:
    frame = next(frames_cycle)
    draw_frame(canvas, row, column, frame)
    await asyncio.sleep(0)
    draw_frame(canvas, row, column, frame, negative=True)

def generate_star_parametres(window_height, window_width, border_size):
  row = random.randint(1, window_height - border_size - 1)
  column = random.randint(1, window_width - border_size - 1)
  symbol = random.choice(STAR_SHAPES)
  return (row, column, symbol)

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
 
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)