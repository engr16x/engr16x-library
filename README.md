# engr16x

[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)

## Introduction

This repository contains the source code for engr16x python package, which houses resources for students of Purdue University enrolled in ENGR16100 / ENGR16200 to use in their completion of projects, assignments, and other activities.

## Library Contents

The engr16x library is orgainized into submodules for ease of use. To import only specific submodules, simply include `import engr16x.name-of-submodule` at the top of any python script. More information on modules can be found [here](https://docs.python.org/3/tutorial/modules.html#packages).

Name | Description
--- | ---
`piTalk` | Allows a Computer to establish a socket connection with a Raspberry Pi and establishes a communication protocol using TCP to send/recieve data from the pi.  For more information see the README.md in this folder
`piTalk.pi` | Submodule of piTalk that contains all the functions to be used by the Raspberry Pi.
`piTalk.computer` | Submondule of piTalk that contains all the functions to be used by the Computer.
`install` | Provides scripts to install python, spyder, and other sofware used in the ENGR16X curriculum.
`projects` | Includes helper files and functions to be used with sensors and motors utilized in projects and in-class activities.

## Repo Structure

Name | Description
--- | ---
`src/engr16x` | Contains all of the source code for the library
`dist` | Contains distribution files used by pip install when installing or upgrading the library
`build/lib` | Source code structure generated during package building.
`engr16x.egg-info` | Metadata relating to installation requirements. Replaced by .whl files in dist, but remains for backwards-compatibility

**Note:** The convention for files and directories in this repository are [snake_case](https://en.wikipedia.org/wiki/Snake_case)!

## Code Standard

In general, follow the [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/). We'll also use the following rules:

### Documentation

- Each Python file should contain the following header.

```python
'''
(Brief description of the module)
---
Example usage:
    (tabbed over code example)
    (or description of how to modify the script)
    (to run it)
'''
```

- Each function should include a [docstring](https://www.python.org/dev/peps/pep-0257/) with a short description of what the function does and its arguments using [Google's convention](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments). For functions with obvious purposes, a one-line docstring is acceptable.

```python
def loadRoster(path):
    '''
    Returns an array represting the roster.

    Args:
        path: path to the Excel file

    Returns:
        Array of the roster in the form [[fullName, username, team], ...]
    '''

    # Code here
```

### Naming

- Use `camelCase` instead of `underscore_case` when naming variables
- Whenever possible, do not use abbreviations for words. For example, use `username` and `password`, not `user` and `pwd`. This does not include initilizations such as `smtp`, `http`, etc.

### Style Choices

- Use single quotes (`'`) instead of double quotes (`"`) unless you would need to escape the quote in a string (example: `"I can't wait"` and `'I can\'t wait'` are good, `"I cannot wait"` is bad)
- Always use `.format()` for strings rather than the `"%d" % (...)` method
- Don't use spaces around the = sign when used to indicate a keyword argument or a default parameter value.

```python
# Good
def complex(real, imag=0.0):
    return magic(r=real, i=imag)

# Bad
def complex(real, imag = 0.0):
    return magic(r = real, i = imag)
```

### Imports

Please note PEP8's comments about [import statements](https://www.python.org/dev/peps/pep-0008/#id23):

> - Imports should usually be on separate lines, e.g.:
>
> ```python
> Yes: import os
>      import sys
>      from subprocess import Popen, PIPE
> No:  import sys, os
> ```
>
> - Imports are always put at the top of the file, just after any module > comments and docstrings, and before module globals and constants. Imports > should be grouped in the following order:
>   - standard library imports
>   - related third party imports
>   - local application/library specific imports
> - You should put a blank line between each group of imports.
