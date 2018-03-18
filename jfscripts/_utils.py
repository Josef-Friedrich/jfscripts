import shutil


def check_executables(*executables):
    errors = []
    for executable in executables:
        if isinstance(executable, tuple):
            if not shutil.which(executable[0]):
                errors.append('{} ({})'.format(executable[0], executable[1]))
        else:
            if not shutil.which(executable):
                errors.append(executable)

    if errors:
        raise SystemError('Some commands are not installed: ' +
                          ', '.join(errors))
