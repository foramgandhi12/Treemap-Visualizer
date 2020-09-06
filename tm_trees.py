"""
=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. It has a concrete implementation of a subclass to represent 
files and folders on the computer's file system.
"""

from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: Optional[str]
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initializes a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, uses <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignores the parameter <data_size>,
        and calculates this tree's data_size instead.

        Sets this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self.data_size = data_size
        self._colour = tuple([randint(0, 255) for _ in range(3)])
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._expanded = False

        # 1. Initializes self._colour and self.data_size, according to the
        # docstring.
        if self._subtrees:
            self.data_size = 0
            for subtree in self._subtrees:
                self.data_size += subtree.data_size

        if self._name is None:
            self._subtrees = []
            self.data_size = 0

        # 2. Sets this tree as the parent for each of its subtrees.
        for subtree in self._subtrees:
            subtree._parent_tree = self

    def is_empty(self) -> bool:
        """Returns True iff this tree is empty.
        """
        return self._name is None

    def get_subtrees(self) -> List[TMTree]:
        """Returns subtrees of TMTree
        """
        return self._subtrees

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Updates the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.

        """
        if self.data_size == 0:
            x, y, width, height = rect
            self.rect = (x, y, 0, 0)
        elif not self._subtrees:
            self.rect = rect
        else:
            self.rect = rect

            x, y, width, height = rect
            subtree_ds = [st.data_size for st in self._subtrees]

            if width > height:
                div_widths = self.__divide_length(width, self.data_size,
                                                  subtree_ds)

                for subtree, div_width in zip(self._subtrees, div_widths):
                    subtree.update_rectangles((x, y, div_width, height))
                    x += div_width
            else:
                div_heights = self.__divide_length(height, self.data_size,
                                                   subtree_ds)

                for subtree, div_height in zip(self._subtrees, div_heights):
                    subtree.update_rectangles((x, y, width, div_height))
                    y += div_height

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Returns a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        lst = []

        if self.__is_in_displayed_tree():
            lst.append((self.rect, self._colour))
        else:
            for subtree in self._subtrees:
                lst += subtree.get_rectangles()

        return lst

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Returns the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, returns the
        tree represented by the rectangle that is closer to the origin.
        """
        leafs = self.__get_nodes_at_position(pos)

        assert 0 <= len(leafs) <= 4

        if not leafs:
            return None
        if len(leafs) == 1:
            return leafs[0]
        else:
            return self.__get_leaf_closest_to_origin(leafs)

    def update_data_sizes(self) -> int:
        """Updates the data_size for this tree and its subtrees, based on the
        size of their leaves, and returns the new size.

        If this tree is a leaf, returns its size unchanged.
        """

        if self.__is_leaf():
            return self.data_size

        else:
            self.data_size = 0

            for subtree in self._subtrees:
                self.data_size += subtree.update_data_sizes()

            return self.data_size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, moves this
        tree to be the last subtree of <destination>. Otherwise, does nothing.
        """

        if self.__is_leaf() and not destination.__is_leaf():
            self._parent_tree._subtrees.remove(self)
            destination._subtrees.append(self)

    def change_size(self, factor: float) -> None:
        """Changes the value of this tree's data_size attribute by <factor>.

        Always rounds up the amount to change, so that it's an int, and
        some change is made.

        Does nothing if this tree is not a leaf.
        """

        if factor > 0:
            self.data_size += math.ceil(self.data_size * factor)
        else:
            amount = self.data_size + math.floor(self.data_size * factor)
            if amount >= 1:
                self.data_size = amount

    def expand(self) -> None:
        if not self.__is_leaf():
            self._expanded = True

    def expand_all(self) -> None:
        self.expand()

        for subtree in self._subtrees:
            subtree.expand_all()

    def collapse(self) -> None:
        if self._parent_tree:
            self._parent_tree._expanded = False

            for subtree in self._parent_tree._subtrees:
                subtree.__collapse_descendants()

    def collapse_all(self) -> None:
        self.collapse()

        if self._parent_tree:
            self._parent_tree.collapse_all()

    # Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Returns a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then adds the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str
        else:
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str

    def get_separator(self) -> str:
        """Returns the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Returns the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError

    def __is_leaf(self) -> bool:
        return not self._subtrees

    def __is_in_displayed_tree(self) -> bool:
        if not self._parent_tree:
            return not self._expanded
        elif self._parent_tree._expanded and not self._expanded:
            return True
        else:
            return False

    def __get_nodes_at_position(self, pos: Tuple[int, int]) -> List[TMTree]:
        if self.__is_in_displayed_tree() and \
                self.__check_pos_in_rect(pos, self.rect):
            return [self]
        else:
            leafs = []
            for subtree in self._subtrees:
                leafs += subtree.__get_nodes_at_position(pos)

            return leafs

    def __collapse_descendants(self) -> None:
        self._expanded = False

        for subtree in self._subtrees:
            subtree.__collapse_descendants()

    @staticmethod
    def __get_leaf_closest_to_origin(leafs: List[TMTree]) -> TMTree:

        for l1 in leafs:
            closest_to_origin = True
            for l2 in leafs:

                if l1 == l2:
                    continue

                l1x, l1y, l1width, l1height = l1.rect
                l2x, l2y, l2width, l2height = l2.rect

                if not (l1x <= l2x and l1y <= l2y):
                    closest_to_origin = False
                    break

            if closest_to_origin:
                return l1

        return None

    @staticmethod
    def __divide_length(total_length: int, total_size: int,
                        sub_sizes: List[int]) -> List[int]:
        div_lens = []
        run_total = 0

        for sub_size in sub_sizes[:-1]:
            div_len = math.trunc(total_length * (sub_size / total_size))
            div_lens.append(div_len)
            run_total += div_len
        div_lens.append(total_length - run_total)

        return div_lens

    @staticmethod
    def __check_pos_in_rect(pos: Tuple[int, int],
                            rect: Tuple[int, int, int, int]) -> bool:
        x, y, width, height = rect
        x_pos, y_pos = pos

        if (x <= x_pos <= (x + width)) and (y <= y_pos <= (y + height)):
            return True
        else:
            return False


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Stores the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        >>> t = FileSystemTree('/Users/foramgandhi/Documents/CSC148')
        >>> t.is_empty()
        'True'
        """

        name = os.path.basename(path)

        if not os.path.isdir(path):
            size = os.path.getsize(path)
            super(FileSystemTree, self).__init__(name, [], size)

        else:
            subtrees = []

            for f_name in os.listdir(path):
                f_path = os.path.join(path, f_name)
                sub_t = FileSystemTree(f_path)
                subtrees.append(sub_t)

            super(FileSystemTree, self).__init__(name, subtrees)

    def get_separator(self) -> str:
        """Returns the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Returns the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
