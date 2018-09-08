# Package Version

Find the version number and other information of the current local installation of engr16x by enetering:

`pip show engr16x`

Version numbering is formatted `major.minor.revision.build` and is incrimented as desribed below.

|  |  |
| --- | --- |
| major | Incrimented when new submodules are added |
| minor | Incrimented when new features or functions within submodules are added |
| revision | Incrimented when existing features or functions are changed to address errors or better performance |
| build | Incrimented when the library is recompiled or other cosmetic changes are made. |

---

# Code Standard

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
