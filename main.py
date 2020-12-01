import asyncio
import curses
import time


TIC_TIMEOUT = 0.1


async def sleep(tics):
  iteration_count = int(tics * 10)

  for _ in range(iteration_count):
    await asyncio.sleep(0)

async def blink(canvas, row, column, symbol='*'):
    while True:
      canvas.addstr(row, column, symbol, curses.A_DIM)
      await sleep(2)

      canvas.addstr(row, column, symbol)
      await sleep(0.3)

      canvas.addstr(row, column, symbol, curses.A_BOLD)
      await sleep(0.5)

      canvas.addstr(row, column, symbol)
      await sleep(0.3)


def draw(canvas):
  canvas.border()
  curses.curs_set(False)

  coroutine_1 = blink(canvas, 1, 1, '*')
  coroutine_2 = blink(canvas, 1, 2, '*')
  coroutine_3 = blink(canvas, 1, 3, '*')
  coroutine_4 = blink(canvas, 1, 4, '*')
  coroutine_5 = blink(canvas, 1, 5, '*')
  coroutines = [coroutine_1, coroutine_2, coroutine_3,
                coroutine_4, coroutine_5]

  while True:
    for coroutine in coroutines:
      coroutine.send(None)

    time.sleep(0.1)
    canvas.refresh()

      
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)