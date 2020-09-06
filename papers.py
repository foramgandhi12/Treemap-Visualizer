"""

=== Module Description ===
This module contains a new class, PaperTree, which is used to model data on
publications in a particular area of Computer Science Education research.
This data is adapted from a dataset presented at SIGCSE 2019.
You can find the full dataset here: https://www.brettbecker.com/sigcse2019/

Although this data is very different from filesystem data, it is still
hierarchical. This means it can be modelled using a TMTree subclass,
and we can then run it through our treemap visualisation tool to get an
interactive graphical representation of the data.

"""
import csv
from typing import List, Dict, Tuple, Optional
from tm_trees import TMTree

# Filename for the dataset
DATA_FILE = 'cs1_papers.csv'


class PaperTree(TMTree):
    """A tree representation of Computer Science Education research paper data.
    
    === Inherited Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.
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
    - All TMTree RIs are inherited.
    """
      
    authors: str
    doi: str

    def __init__(self, name: str, subtrees: List[TMTree], authors: str = '',
                 doi: str = '', citations: int = 0, by_year: bool = True,
                 all_papers: bool = False) -> None:
        """Initializes a new PaperTree with the given <name> and <subtrees>,
        <authors> and <doi>, and with <citations> as the size of the data.

        If <all_papers> is True, then this tree is to be the root of the paper
        tree. In that case, load data about papers from DATA_FILE to build the
        tree.

        If <all_papers> is False, Do NOT load new data.

        <by_year> indicates whether or not the first level of subtrees should be
        the years, followed by each category, subcategory, and so on. If
        <by_year> is False, then the year in the dataset is simply ignored.
        """
        self.authors = authors
        self.doi = doi

        if all_papers:
            nested_dict = _load_papers_to_dict(by_year)
            subtrees = _build_tree_from_dict(nested_dict)

        super(PaperTree, self).__init__(name, subtrees, citations)

    def get_separator(self) -> str:
        """Returns the file separator for this OS.
        """
        return '/'

    def get_suffix(self) -> str:
        """Returns the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (paper)'
        else:
            return ' (category)'


def _load_papers_to_dict(by_year: bool = True) -> Dict:
    """Returns a nested dictionary of the data read from the papers dataset file.

    If <by_year>, then uses years as the roots of the subtrees of the root of
    the whole tree. Otherwise, ignores years and uses categories only.
    """
      
    cat_dict = {}

    with open(DATA_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        # skips first row of column names
        next(csv_reader)

        for row in csv_reader:
            authors = row[0]
            name = row[1]
            year = row[2]
            categories = row[3].split(': ')
            doi = row[4]
            citations = int(row[5])

            paper = (authors, name, doi, citations)

            if by_year:
                if year not in cat_dict:
                    cat_dict[year] = {}

                _add_paper_to_dict(cat_dict[year], categories, paper)
            else:
                _add_paper_to_dict(cat_dict, categories, paper)

    return cat_dict


def _build_tree_from_dict(nested_dict: Dict) -> List[PaperTree]:
    """Returns a list of trees from the nested dictionary <nested_dict>."""

    subtrees = []
    for key in nested_dict:
        # creates leaf nodes for papers
        if key == '':
            papers = nested_dict['']

            # paper: (authors, name, doi, citations)
            for paper in papers:
                subtrees.append(
                    PaperTree(paper[1], [], paper[0], paper[2], paper[3])
                )
        # creates internal node for category
        else:
            trees = _build_tree_from_dict(nested_dict[key])
            subtrees.append(PaperTree(key, trees))

    return subtrees


def _add_paper_to_dict(old_dict: Dict, categories: List[str],
                       paper: Tuple[str, str, str, int]) -> None:
    cur_dict = old_dict
    for category in categories:
        if category not in cur_dict:
            cur_dict[category] = {}

        cur_dict = cur_dict[category]

    if '' not in cur_dict:
        cur_dict[''] = []

    cur_dict[''].append(paper)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': ['python_ta', 'typing', 'csv', 'tm_trees'],
        'allowed-io': ['_load_papers_to_dict'],
        'max-args': 8
    })
