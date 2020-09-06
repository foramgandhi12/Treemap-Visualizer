import os


def print_items(d: str, indentation: str) -> None:
    """A sample program showing how to recurse on directories using os.

    Prints the list of files and directories in directory <d>, recursively,
    prefixing each with the given <indentation>.
    """
    print(indentation + d + ':')
    for filename in os.listdir(d):
        print(indentation + filename)
        subitem = os.path.join(d, filename)
        if os.path.isdir(subitem):
            print_items(subitem, indentation + '    ')


if __name__ == '__main__':
    # Put in a path like
    # 'C:\\Users\\Bogdan\\Documents\\csc148\\assignments' (Windows) or
    # '/Users/Bogdan/Documents/courses/csc148/assignments' (OSX)
    # to print the contents of that folder.
    print_items(INSERT_PATH_HERE, '')
