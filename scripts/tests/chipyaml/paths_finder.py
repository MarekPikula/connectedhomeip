#!/usr/bin/env -S python3 -B
# Copyright (c) 2023 Project CHIP Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
import os
import tempfile
from pathlib import Path
from queue import Queue

import click

log = logging.getLogger(__name__)

_PATHS_CACHE_NAME = 'yaml_runner_cache'
try:
    from diskcache import Cache
    _paths_cache = Cache(Path(tempfile.gettempdir()) / _PATHS_CACHE_NAME)
except ImportError:
    _paths_cache = {}
_PATH_NOT_FOUND = "//NOT_FOUND//"
_path_check_queue: Queue[str] = Queue()

DEFAULT_CHIP_ROOT = Path(__file__).parent.parent.parent.parent.absolute()


def queue_find_file_path(target_name: str):
    global _path_check_queue
    _path_check_queue.put(target_name)


def find_file_path(target_name: str, try_again: bool = False) -> Path | None:
    """Find file path and cache the result.

    Arguments:
        target_name -- target file name

    Keyword Arguments:
        try_again -- try again if cached as not found (default: {False})

    Returns:
        Valid file path if file exists or None if not found.
    """
    global _paths_cache, _path_check_queue

    # First check if it already exists in cache.
    if (path_cached := _paths_cache.get(target_name)) is not None:
        if path_cached == _PATH_NOT_FOUND and not try_again:
            return None

        if isinstance(path_cached, str) and (path := Path(path_cached)).is_file():
            return path

        del _paths_cache[target_name]

    # Flush path check queue.
    targets_to_find = [target_name]
    while not _path_check_queue.empty():
        targets_to_find.append(_path_check_queue.get())

    # Walk the filesystem looking for all target paths in the queue.
    log.debug("Looking for app path for '%s'", target_name)
    targets_to_add = {target: Path(dirpath) / target
                      for dirpath, _, filenames in os.walk(DEFAULT_CHIP_ROOT)
                      for target in targets_to_find
                      if target in filenames}

    # Add all targets either as found or not found.
    for target in targets_to_find:
        target_path = targets_to_add.get(target)
        _paths_cache[target] = _PATH_NOT_FOUND if target_path is None else str(target_path)

    # Return result for this request.
    return targets_to_add.get(target_name)


def clear_cache() -> None:
    global _paths_cache
    for key in _paths_cache:
        del _paths_cache[key]


@click.group()
def finder():
    pass


@finder.command()
def view():
    """View the cache entries."""
    global _paths_cache

    if len(tuple(_paths_cache.iterkeys())) == 0:
        print("Cache is empty.")
        return

    name_max_len = max(len(str(name)) for name in _paths_cache)
    for name in _paths_cache:
        print(click.style(f'{name}: ', bold=True) + (" "*(name_max_len-len(str(name)))) + str(_paths_cache[name]))


@finder.command()
@click.argument('key', type=str)
@click.argument('value', type=str)
def add(key: str, value: str):
    """Add a cache entry."""
    global _paths_cache
    _paths_cache[key] = value


@finder.command()
@click.argument('name', type=str)
def delete(name: str):
    """Delete a cache entry."""
    global _paths_cache
    if name in _paths_cache:
        del _paths_cache[name]


@finder.command()
def reset():
    """Delete all cache entries."""
    clear_cache()


@finder.command()
@click.argument('name', type=str)
def search(name: str):
    """Search for a target and add it to the cache."""
    if (path := find_file_path(name)) is not None:
        print(f'The target "{name}" has been added with the value "{path}".')
    else:
        print(f'The target "{name}" was not found.')


if __name__ == '__main__':
    finder()
