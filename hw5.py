from typing import Dict, List, Optional, Set, Tuple

Metadata = Dict[int, Tuple[str, str]]
FileSizes = Dict[int, int]
DirContent = Dict[int, List[int]]

# I want to thank zou for your good reviews
# it really helped me to understand recursion properly
# and use it in right way in hw6


class Node:
    def __init__(self, nid: int, name: str, owner: str,
                 is_dir: bool, size: int, parent: Optional['Node'],
                 children: List['Node'], children_num: List[int]):
        self.nid = nid
        self.name = name
        self.owner = owner
        self.is_dir = is_dir
        self.size = size
        self.parent = parent
        self.children = children
        self.children_num = children_num  # list of children nids

    def is_valid(self) -> bool:
        node: 'Node' = self
        root = self.find_root(node)

        # name of any node is not empty except the root node
        if root.owner == '' or '/' in root.name:
            return False
        # owner of any node is not empty
        # no directory contains two nodes with the same name
        return self.is_valid_child(root.children)

    def find_root(self, root) -> 'Node':
        if root is not None:
            while root.parent is not None:
                root = root.parent
        return root

    def is_valid_child(self, children: List['Node']) -> bool:
        for child in children:
            # name of any node not consist of (/) or owner or name is not empty
            if '/' in child.name or child.owner == '' or child.name == '':
                return False

        # check if there is any duplicate nid in children (directory)
        children_name = [child.name for child in children]
        if len(set(children_name)) != len(children_name):
            return False

        # recursively call is_valid_child() on all children..
        for child in children:
            # any of them is False -> False
            if not self.is_valid_child(child.children):
                return False
        # this file system is valid
        return True

    def draw(self) -> None:
        body: List[str] = []
        # start with printing current file
        print('-- ' + self.name)

        # draw_body() is returning list of strings
        # -> together they're making a text representation of a file system
        if self.children:
            self.draw_body(self.children, count=0, space='')

    def draw_body(self, children: List['Node'], count, space) -> List[str]:

        space_dir = '    '
        tab = '   |'
        end_tab = '   \\'

        if count > 0:
            space += space_dir
        count += 1
        for i, child in enumerate(children):

            # last file?
            if i == len(children) - 1:
                print(space + end_tab + '-- ' + child.name)
            else:
                print(space + tab + '-- ' + child.name)

            if (child.is_dir and i == len(children) - 1) or child.is_dir:
                self.draw_body(child.children, count, space)

    # return full path to current node
    # BASE: current directory is None
    # STEP: getting closer to the root
    def full_path(self) -> str:
        current_node = self
        if current_node.parent is not None:
            if current_node.is_dir:
                full_path = self.find_path(current_node, '') + '/'
                return full_path
            full_path = self.find_path(current_node, '')
            return full_path
        # empty path
        return '/'

    def find_path(self, node, path):
        # BASE
        if node.parent is None:
            return path
        # building path, root will be first
        current_node = "/" + node.name
        current_node += path
        path = current_node
        # STEP, node.parent
        return self.find_path(node.parent, path)

    # return (number of files, sum of all file sizes)
    # BASE: current node is a file
    # STEP: search for a files (in childrens),
    # we are closer to the point where there are no childrens
    def disk_usage(self) -> Tuple[int, int]:
        disk_info = self.disk_traverse(self, [])
        return (disk_info[0], sum(disk_info[1]))

    def disk_traverse(self, parent: 'Node', size) -> Tuple[int, int]:
        # BASE
        # if parent is a file
        if not parent.is_dir:
            return (1, [parent.size])
        for child in parent.children:
            # STEP, child
            # print(size)
            size = size + self.disk_traverse(child, [])[1]
            # when child.children is not empty
        return (len(size), size)

    # return a set of all owners (all nodes from a current node (including))
    # BASE:
    # STEP: getting closer to the node without children
    def all_owners(self) -> Set[str]:
        # start with a current file owner and empty set
        return self.owners_traverse(self, set())

    def owners_traverse(self, parent: 'Node', owners: Set[str]) -> Set[str]:
        owners.add(self.owner)
        for child in parent.children:
            owners.add(child.owner)
            if child.is_dir:
                # STEP, child
                self.owners_traverse(child, owners)
        return owners

    # return list of all empty files from current node
    # BASE: current node is an empty file
    # STEP: getting closer to the node without children
    def empty_files(self) -> List['Node']:
        return self.search_empty(self, [])

    def search_empty(self, parent: 'Node',
                     empty_fl: List['Node']) -> List['Node']:
        # BASE, empty file
        if not parent.is_dir and parent.size == 0:
            empty_fl.append(parent)
        # traverse through the list of parents of current node
        for child in parent.children:
            if not child.is_dir and child.size == 0:
                empty_fl.append(child)
            else:
                self.search_empty(child, empty_fl)
        return empty_fl

    # 5.
    def prepend_owner_name(self) -> None:
        if not self.is_dir:
            self.name = self.owner + '_' + self.name
        self.rename_files(self.children)
        return None

    def rename_files(self, children: List['Node']) -> None:
        for child in children:
            if not child.is_dir:
                child.name = child.owner + '_' + child.name
                child.name
            else:
                self.rename_files(child.children)
        return None

    def add_keep_files(self, start: int) -> None:
        # if current file is an empty directory append keep file
        keep_nid = start
        if not self.children and self.is_dir:
            self.children.append(Node(keep_nid, ".keep",
                                      self.owner,
                                      False, 0, self, [],
                                      []))
        else:
            self.add_files(self, keep_nid)
        return None

    def add_files(self, parent: 'Node', keep_nid: int) -> int:
        for child in parent.children:
            # child is an empty directory -> insert child
            if child.is_dir and not child.children:
                child.children.append(Node(keep_nid, ".keep",
                                           child.owner,
                                           False, 0, child, [],
                                           []))
                keep_nid += 1
                self.add_files(child, keep_nid)
            # child is a directory
            elif child.is_dir:
                # -> search it for empty directories
                keep_nid = self.add_files(child, keep_nid)  # update keep_nid
        return keep_nid

    # 6.
    def remove_empty_dirs(self) -> None:
        if self.is_dir and len(self.children) == 0:
            pass
        else:
            initial_dir = self
            self.remove_empty(self, initial_dir)

    def remove_empty(self, parent: 'Node', initial_dir: 'Node') -> None:
        for child in parent.children:
            if child.is_dir and not child.children:
                parent.children.remove(child)
                if not parent.children:
                    return self.remove_empty(initial_dir, initial_dir)
                return self.remove_empty(parent, initial_dir)
            if child.is_dir:
                self.remove_empty(child, initial_dir)
        return None

    def remove_all_foreign(self, user: str) -> None:
        self.remove_all(self, user)

    def remove_all(self, parent: 'Node', user: str) -> None:
        for child in parent.children:
            if child.owner != user:
                parent.children.remove(child)
                return self.remove_all(parent, user)
            if child.is_dir:
                self.remove_all(child, user)
        return None


def build_fs(metadata: Metadata,
             file_sizes: FileSizes,
             dir_content: DirContent) -> Optional[Node]:
    # build_fs2(), 1., 2., 3.

    # 3. if there is no nodes, there is no root -> None
    if not metadata:
        return None

    # when root is the only node
    # and dir_content is empty
    # its an empty directory
    if not dir_content and len(metadata) == 1:
        # print('ss')
        for nid in metadata:
            name = metadata[nid][0]
            owner = metadata[nid][1]
        # return empty root directory
        root = Node(nid, name, owner, True, 0, None, [], [])
        return root

    # 2. file_sizes and dir_content dont have any nid in common else -> None
    # file_sizes ∩ dir_content = ∅
    if set(file_sizes.keys()).\
            intersection(set(dir_content.keys())) != set():
        # print("* 2")
        return None

    # list of children lists (dir_content values)
    dir_content_values = dir_content.values()

    # create a list of all child nids
    dir_content_vals = []
    for dirs in dir_content_values:
        for nid in dirs:
            dir_content_vals.append(nid)

    # 1. metadata contains every nid from file_sizes
    #   or dir_content else -> None

    # list of file_sizes keys + union of
    # all nids (keys and values) from dir_content
    file_and_dir = list(file_sizes.keys()) + \
        list(set(dir_content.keys()).union(set(dir_content_vals)))
    # only dir_content nids
    dir_nids = set(dir_content.keys()).union(set(dir_content_vals))
    meta_keys = list(metadata.keys())
    # when meta_keys / file_and_dir isn't ∅ -> None
    # when meta_keys / dir_nids isn't ∅
    # -> if only one root exists, metadata have more nodes then dir_content
    # -> there are more then one root -> None
    # print(set(meta_keys))
    if set(file_and_dir).difference(set(meta_keys)) != set() or\
            set(meta_keys).difference(set(dir_nids)) != set():
        # print("* 1")
        return None

    count_roots = 0
    # traverse through dir_content keys, searching for root
    for nid in dir_content:
        name = metadata[nid][0]
        owner = metadata[nid][1]
        # when nid isnt children of anyone
        # print(count_roots)
        if nid not in dir_content_vals and count_roots == 0:
            # create root directory
            root = Node(nid, name, owner, True, 0,
                        None, [], dir_content[nid])
            count_roots += 1
            # prepare class argument
        # 3. always only one root exist (node without parent) else -> None
        elif nid not in dir_content_vals and count_roots > 0:
            # print("* 3")
            return None

    # search for childs
    root_node = search_childs(
        root, metadata, file_sizes, dir_content)
    return root_node  # return a whole file system


def search_childs(parent: Node,
                  metadata: Dict[int, Tuple[str, str]],
                  file_sizes: Dict[int, int],
                  dir_content: Dict[int, List[int]]) -> Node:
    # print('here')
    # search for parent childrens in dir_content
    # and build a file system
    parent_child = []  # current directory
    for child_nid in parent.children_num:
        name = metadata[child_nid][0]
        owner = metadata[child_nid][1]
        # not in dir_content
        if child_nid not in dir_content:
            # but in file_sizes
            if child_nid in file_sizes:
                # create children (file)
                parent_child.\
                    append(Node(child_nid, name,
                                owner, False,
                                file_sizes[child_nid],
                                parent, [], []))
            # not in dir_content nor in file_sizes
            # its an empty directory
            else:
                parent_child.\
                    append(Node(child_nid, name,
                                owner, True,
                                0, parent, [], [], ))
        # its in dir_content as a key
        else:
            # create children (directory)
            # and search for its files
            full_child = search_childs(Node(child_nid, name, owner,
                                            True, 0, parent, [],
                                            dir_content[child_nid],
                                            ), metadata,
                                       file_sizes, dir_content)
            # add it to current directory
            parent_child.append(full_child)

    parent.children = parent_child
    return parent


def test_root_only() -> None:
    root = build_fs({1: ("", "root")}, {}, {})
    assert root is not None
    assert root.nid == 1
    assert root.name == ""
    assert root.owner == "root"
    assert root.is_dir
    assert root.size == 0
    assert root.parent is None
    assert root.children == []
    assert root.is_valid()
    # print(root.full_path())
    assert root.full_path() == "/"
    assert root.disk_usage() == (0, 0)
    assert root.all_owners() == {"root"}
    assert root.empty_files() == []


def test_example() -> None:
    # is_valid()
    # jméno žádného uzlu kromě kořenového není prázdné;
    # jméno žádného uzlu neobsahuje znak lomítko (/);
    # vlastník žádného uzlu není prázdný;
    # žádný adresář neobsahuje dva uzly stejného jména.

    # MY TESTS #
    # root_test0 = build_fs({420: ('bor', 'br')}, {420: 420}, {})
    # root_test0.draw()

    root_disk = root = build_fs(
        {-2: ('0', '0'), -1: ('0', '0'), 0: ('0', '0'),
         1: ('.', '0'), 2: ('', '0'), 420: ('tyrek', 'rir')},
        {-2: 0, 420: 420},
        {-1: [0, 1], 1: [-2, 420], 2: [-1]})
    # root_disk.draw()
    print(root_disk.disk_usage())

    root = build_fs(
        {-91: ('usr', 'leela'), -79: ('.XCompose', 'fry'), -6: ('', 'fry'), -45:
         ('mnt', 'amy'), -7: ('run', 'leela')},
        {-79: 1337},
        {-45: [], -91: [-45], -6: [-7], -7: [-91, -79]})
    print(root.disk_usage())

    root = build_fs(
        {-1: ('root', 'fry'), 21: ('mnt', 'fry'), -15: ('list_nice.txt', 'amy'),
         25: ('root', 'amy'), 94: ('', 'fry'), -85: ('mnt', 'fry'), -62: ('mnt',
                                                                          'bender'), 48: ('var', 'amy'), -30: ('.XCompose', 'bender'), -52:
            ('list_naughty.txt', 'bender'), 54: ('bin', 'amy'), 1: ('mnt', 'bender'), -58:
            ('list_nice.txt', 'leela'), -57: ('root', 'bender'), 3: ('bin', 'bender'), 15:
            ('mnt', 'leela'), -61: ('var', 'amy'), 80: ('var', 'fry'), 43: ('mnt', 'amy'),
            -76: ('bin', 'fry'), 68: ('var', 'amy'), 99: ('root', 'fry'), -40: ('run',
                                                                                'leela'), -31: ('run', 'amy'), 91: ('mnt', 'leela'), 63: ('var', 'leela'), -72:
            ('usr', 'leela'), 61: ('mnt', 'bender'), 77: ('var', 'leela'), -51: ('bin',
                                                                                 'fry'), 8: ('bin', 'fry')},
        {-58: 420, -52: 0, -15: 1337, -30: 1337},
        {-40: [15, 77], 54: [48, 91], 80: [-15, -52], -62: [68, 21], 43: [], 1:
         [-58, -57], -61: [-1, -76], -51: [99, -31], 61: [], 25: [-72, 61], 63: [-85,
                                                                                 3], -85: [], 8: [-30, 43], -76: [-40, 54], -1: [-62, 63], -72: [], -31: [8,
                                                                                                                                                          25], 99: [80, 1], 94: [-61, -51], -57: []})
    print(root.all_owners())

    """
    root_owners = root = build_fs(
        {64: ('mnt', 'leela'), 21: ('mnt', 'amy'), 84: ('root', 'bender'), 46:
         ('', 'leela'), -12: ('bin', 'amy')}, {},
        {21: [],
         84: [21],
         46: [64],
         64: [-12, 84]})
    print(root_owners)
    # root_owners.draw()
    # print(root_owners.all_owners())

    root_keep = build_fs({-1: ('rys', 'root'),
                          0: ('0', 'root'), 1: ('.', 'root'),
                          4: ('terion', 'liba'),
                          420: ('bakelyt', 'frantik'),
                          520: ('sumatra', 'frantik'), 244: ('kokot', 'o')},
                         {520: 12312032139}, {-1: [0, 1, 420], 1: [4, 520], 420: [244]})

    root_keep.add_keep_files(2)

    root_keep.draw()
    # print()
    # print(root_keep.children[1].children[0].children[0].nid)
    # assert len(root_keep.children[1].children) == 1
    """
    root_testA = root = build_fs(
        {1: ('', '')},
        {},
        {1: [0]})
    assert root_testA is None
    # assert root_testA.is_valid()
    # root_testA.draw()

    root_test = example_fs()
    # print(root_test.children[0].children[0].full_path())
    print(root_test.children[0].disk_usage())
    assert root_test.children[0].disk_usage() == (3, 1084040)

    print(root_test.children[0].children[0].disk_usage())
    assert root_test.children[0].children[0].disk_usage() == (1, 141936)

    assert len(root_test.children[0].children[2].empty_files()) == 0

    root_test.children[3].add_keep_files(7000)
    assert len(root_test.children[3].children) == 1

    root_test2 = example_fs()
    root_test2.children[3].remove_empty_dirs()
    # print(len(root_test2.children))
    # print()
    # root_test2.draw()
    assert len(root_test2.children) == 4

    root_test3 = example_fs()
    root_test3.children[2].children[0].children[1].remove_empty_dirs()
    # print(len(root_test3.children[2].children[0].children))
    # print()
    # root_test3.draw()
    assert len(root_test3.children[2].children[0].children) == 2

    root_test6 = example_fs()
    root_test6.children[2].remove_empty_dirs()
    # print(len(root_test6.children[2].children[0].children))
    # print()
    # root_test6.draw()
    assert len(root_test6.children[2].children[0].children) == 1

    root_test7 = example_fs()
    root_test7.remove_empty_dirs()
    # root_test7.draw()

    root_test4 = example_fs()
    root_test4.children[0].children[2].prepend_owner_name()
    # root_test4.draw()

    root_test5 = example_fs()
    root_test5.children[3].remove_empty_dirs()

    # root1 = build_fs({1: ('MY_FS', ''), 2: ('tmp', 'nobody')}, {}, {1: [2]})
    # print(root1)
    # assert root1.children[0].is_valid() is False

    root2 = build_fs({1: ('MY_FS', 'rys'), 2: ('tmp', 'nobody'),
                      3: ('tmp', 'nobody')}, {3: 100}, {1: [2]})
    assert root2 is None
    # assert root2.is_valid()
    # root2.draw()

    # root3 = build_fs({1: ('bor', 'br'), 2: ('tmp', 'nobody'),
    #                   3: ('tmp', 'nobody')}, {}, {1: [2], 2: [3]})
    # assert root3.is_valid()

    root5 = build_fs({1: ('bor', 'br'), 2: ('tmp', 'nobody'),
                      3: ('tmp', 'nobody')}, {}, {1: [2], 2: []})
    assert root5 is None
    root2 = build_fs({0: ('', '0'), 1: ('0', '0'),
                      420: ('rys', ''), 5: ('porek', 'rys')}, {1: 0}, {0: [1]})
    assert root2 is None
    # root2.draw()

    root4 = build_fs(
        {0: ('', ''), 1: ('', '')}, {}, {1: []})
    assert root4 is None

    root5 = build_fs({}, {}, {})
    assert root5 is None

    root6 = build_fs({0: ('', '0'), 1: ('0', '0')}, {1: 0}, {0: [1]})
    assert root6 is not None

    ##############################
    root = example_fs()
    # print(root.children_num)
    assert root is not None
    assert root.name == 'MY_FS'
    assert root.owner == 'root'
    home = root.children[2]
    assert home.name == 'home'
    assert home.owner == 'root'
    ib111 = home.children[0].children[0]
    assert ib111.name == 'ib111'
    assert ib111.owner == 'user'
    assert ib111.is_dir

    assert len(ib111.children[0].children) == 4
    python = root.children[0].children[1]
    assert python.name == 'python'
    assert python.owner == 'root'
    assert python.size == 14088
    assert not python.is_dir
    assert root.children[3].is_dir

    assert ib111.parent is not None
    assert ib111.parent.parent == home

    assert ib111.is_valid()
    assert python.is_valid()
    python.name = ""
    assert not ib111.is_valid()
    python.name = "python"

    assert python.full_path() == '/bin/python'
    assert ib111.children[0].full_path() == '/home/user/ib111/reviews/'

    print(root.disk_usage())
    assert root.disk_usage() == (8, 1210022)
    assert home.disk_usage() == (4, 78326)

    print(root.all_owners())
    assert root.all_owners() == {'nobody', 'user', 'root'}
    assert home.all_owners() == {'user', 'root'}
    assert python.all_owners() == {'root'}

    empty = ib111.children[0].children[3]
    assert empty.name == '.timestamp'
    assert root.empty_files() == [empty]

    root.prepend_owner_name()
    print(python.name)
    assert python.name == 'root_python'
    assert empty.name == 'user_.timestamp'
    # print(root.children[0].children[2].name)
    root.add_keep_files(7000)

    keep1 = root.children[-1].children[0]
    assert keep1.name == '.keep'
    assert keep1.size == 0
    assert not keep1.is_dir

    keep2 = home.children[0].children[1].children[0].children[0]
    assert keep2.name == '.keep'
    assert keep2.size == 0
    assert not keep2.is_dir

    empty_files = root.empty_files()
    assert len(empty_files) == 3
    assert empty in empty_files
    assert keep1 in empty_files
    assert keep2 in empty_files

    """
    assert keep1.nid + keep2.nid == 7000 + 7001
    root1 = build_fs({1: ('MY_FS', ''), 2: ('tmp', 'nobody')}, {}, {1: [2]})
    assert not root1.is_valid()
    ###
    root2 = build_fs({1: ('MY_FS', '')}, {}, {})
    print(root1)
    assert not root1.is_valid()
    """
    # root.children[0].children[2].draw()


def draw_example() -> None:
    root = example_fs()
    print("První příklad:")
    root.draw()
    print("\nDruhý příklad:")
    root.children[2].draw()

    print("\nPrvní příklad, po použití root.remove_empty_dirs():")
    root = example_fs()
    root.remove_empty_dirs()
    root.draw()

    print("\nPrvní příklad, po použití root.remove_all_foreign('root'):")
    root = example_fs()
    root.remove_all_foreign('root')
    root.draw()

    print("\nPrvní příklad, po použití root.remove_all_foreign('nobody'):")
    root = example_fs()
    root.remove_all_foreign('nobody')
    root.draw()


def example_fs() -> Node:
    root = build_fs(
        {
            1: ("MY_FS", "root"),
            17: ("bash", "root"),
            42: ("bin", "root"),
            9: ("ls", "root"),
            11: ("python", "root"),
            20: ("usr", "root"),
            1007: ("bin", "root"),
            1100: ("env", "root"),
            999: ("home", "root"),
            2001: ("ib111", "user"),
            25: ("user", "user"),
            2002: ("reviews", "user"),
            3000: ("review1.txt", "user"),
            3017: ("review2.txt", "user"),
            3005: ("review3.txt", "user"),
            100: ("tmp", "nobody"),
            2003: ("pv264", "user"),
            3001: ("projects", "user"),
            1234: (".timestamp", "user"),
        },
        {
            9: 141936,
            11: 14088,
            1100: 47656,
            17: 928016,
            3000: 11660,
            3017: 12345,
            3005: 54321,
            1234: 0,
        },
        {
            42: [9, 11, 17],
            20: [1007],
            1007: [1100],
            999: [25],
            25: [2001, 2003],
            2001: [2002],
            1: [42, 20, 999, 100],
            2002: [3000, 3017, 3005, 1234],
            2003: [3001],
        })

    assert root is not None
    return root


if __name__ == '__main__':
    # test_root_only()
    test_example()
    draw_example()  # uncomment to run
