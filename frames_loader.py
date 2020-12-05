
from os import listdir, path


def load_frame_from_file(filename):
  with open(filename, 'r') as fn:
    return fn.read()


def load_frames_from_dir(dirname):
  return [
    load_frame_from_file(path.join(dirname, filename))
    for filename in listdir(dirname)
    if path.isfile(path.join(dirname, filename))
  ]