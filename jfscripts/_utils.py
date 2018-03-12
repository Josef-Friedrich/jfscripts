import shutil


def check_executables(*executables):
    errors = []
    for executable in executables:
        if not shutil.which(executable):
            errors.append(executable)

    if errors:
        raise SystemError('Some commands are not installed: ' +
                          ' '.join(errors))
