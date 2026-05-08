# Copyright (c) 2026 Project CHIP Authors
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

import os
from pathlib import Path

PW_PROJECT_ROOT = Path(path).absolute() if (path := os.getenv("PW_PROJECT_ROOT")) is not None else None
PW_ENVIRONMENT_ROOT = Path(path).absolute() if (path := os.getenv("PW_ENVIRONMENT_ROOT")) is not None else None

if (chip_root := os.getenv("DEFAULT_CHIP_ROOT")) is not None:
    DEFAULT_CHIP_ROOT = Path(chip_root).absolute()
elif PW_PROJECT_ROOT is not None:
    DEFAULT_CHIP_ROOT = PW_PROJECT_ROOT
elif PW_ENVIRONMENT_ROOT is not None:
    DEFAULT_CHIP_ROOT = PW_ENVIRONMENT_ROOT.parent
else:
    raise OSError(
        "Unable to determine the default CHIP root directory. Please set the DEFAULT_CHIP_ROOT environment variable or ensure that "
        "PW_PROJECT_ROOT or PW_ENVIRONMENT_ROOT is set."
    )
