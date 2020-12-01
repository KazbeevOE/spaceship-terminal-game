import asyncio
import curses
import time
import random


TIC_TIMEOUT = 0.1
STAR_SHAPES = '+*.:'

def draw(canvas):
  window_height, window_width = canvas.getmaxyx()
  max_amount_of_stars = random.randint(50, 100)
  border_size = 1

  canvas.border()
  curses.curs_set(False)
  canvas.refresh()

  coroutines = []

  for s in range(max_amount_of_stars):
    row, column, symbol = generate_star_parametres(window_height, window_width, border_size)
    delay = random.randint(0, 3)
    coroutine = blink(canvas, row, column, symbol, delay)
    coroutines.append(coroutine)

  while True:
    for coroutine in coroutines:
      coroutine.send(None)

    time.sleep(0.1)
    canvas.refresh()

def generate_star_parametres(window_height, window_width, border_size):
  row = random.randint(1, window_height - border_size - 1)
  column = random.randint(1, window_width - border_size - 1)
  symbol = random.choice(STAR_SHAPES)
  return (row, column, symbol)

async def blink(canvas, row, column, symbol='*', delay=0):
  while True:
    if delay == 0:
      canvas.addstr(row, column, symbol, curses.A_DIM)
      await sleep(2)
      delay += 1

    if delay == 1:
      canvas.addstr(row, column, symbol)
      await sleep(0.3)
      delay += 1

    if delay == 2:
      canvas.addstr(row, column, symbol, curses.A_BOLD)
      await sleep(0.5)
      delay += 1
    
    if delay == 3:
      canvas.addstr(row, column, symbol)
      await sleep(0.3)
      delay = 0

async def sleep(tics):
  iteration_count = int(tics * 10)

  for _ in range(iteration_count):
    await asyncio.sleep(0)
 
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)