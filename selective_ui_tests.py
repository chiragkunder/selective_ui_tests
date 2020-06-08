import glob
import os

import anytree
from anytree import AnyNode, RenderTree
from git import Repo

SRC_JAVA_PATTERN = "src/main/java/"
SRC_JAVA_TEST_PATTERN = "src/test/java/"
SRC_JAVA_ANDROID_TEST_PATTERN = "src/androidTest/java/"
SRC_JAVA_ANDROID_TEST_PATTERN = "src/androidTest/java/"
SRC_KOTLIN_PATTERN = "src/main/kotlin/"
SRC_KOTLIN_TEST_PATTERN = "src/test/kotlin/"
SRC_KOTLIN_ANDROID_TEST_PATTERN = "src/androidTest/kotlin/"

JAVA_EXTENSION = ".java"
KOTLIN_EXTENSION = ".kt"


def selective_ui_tests():
    repo = Repo()
    diff = repo.git.diff(name_only=True).split("\n")
    return selective_ui_tests_with_diff(diff)


def selective_ui_tests_with_diff(diff):
    if not diff:
        raise ValueError("No files changed!")
    return [_find_all_ui_tests(source, SRC_JAVA_ANDROID_TEST_PATTERN) for source in diff]


def _find_all_ui_tests(source_path, pattern, project_path=None):
    """ Function to find all dependent ui tests for given source.  """
    if not project_path:
        project_path = os.getcwd()

    package_name = _extract_package_name_from_path(source_path)
    root = AnyNode(package_name=package_name, path=source_path)

    tree = _build_source_dependency_tree(root, package_name, _get_source_files_in_folder(project_path))

    results = anytree.search.findall(tree, filter_=lambda n: pattern in str(n.path))

    return [result.package_name for result in results]


def _build_source_dependency_tree(root, package_name, all_source_files):
    """ Function to build a dependency tree for single source file. """
    for pathname in all_source_files:
        source_file = open(pathname)
        imports = _read_imports_from_source(source_file)
        if package_name in imports:
            next_package_name = _extract_package_name_from_path(source_file.name)
            node = AnyNode(package_name=next_package_name, path=source_file.name)
            source_file.close()
            child = _build_source_dependency_tree(node, next_package_name, all_source_files)
            child.parent = root

    return root


def _get_all_source_files_in_project(project_path):
    kt_files = glob.glob(project_path + '/**/*.kt', recursive=True)
    java_files = glob.glob(project_path + '/**/*.java', recursive=True)
    return kt_files + java_files


def _get_source_files_in_folder(folder_path):
    kt_files = glob.glob(folder_path + '*.kt', recursive=False)
    java_files = glob.glob(folder_path + '*.java', recursive=False)
    return kt_files + java_files


def _print_tree(tree):
    for pre, fill, node in RenderTree(tree):
        print("%s%s" % (pre, node.package_name))


def _read_imports_from_source(file):
    imports = list(filter(_is_import, file.readlines()))
    imports = [line.replace("import", "") for line in imports]
    imports = [line.strip() for line in imports]
    return imports


def _is_import(line):
    return line.startswith('import')


def _extract_package_name_from_path(source_path):
    if SRC_JAVA_PATTERN in source_path:
        package_name = source_path.split(SRC_JAVA_PATTERN, 1)[1]
    elif SRC_JAVA_TEST_PATTERN in source_path:
        package_name = source_path.split(SRC_JAVA_TEST_PATTERN, 1)[1]
    elif SRC_JAVA_ANDROID_TEST_PATTERN in source_path:
        package_name = source_path.split(SRC_JAVA_ANDROID_TEST_PATTERN, 1)[1]
    elif SRC_KOTLIN_PATTERN in source_path:
        package_name = source_path.split(SRC_KOTLIN_PATTERN, 1)[1]
    elif SRC_KOTLIN_TEST_PATTERN in source_path:
        package_name = source_path.split(SRC_KOTLIN_TEST_PATTERN, 1)[1]
    elif SRC_KOTLIN_ANDROID_TEST_PATTERN in source_path:
        package_name = source_path.split(SRC_KOTLIN_ANDROID_TEST_PATTERN, 1)[1]
    else:
        raise ValueError("The source file should be Java or Kotlin. Found = {%s}" % source_path)

    return package_name \
        .replace("/", ".") \
        .replace(JAVA_EXTENSION, "") \
        .replace(KOTLIN_EXTENSION, "")


input_diff = input("Enter list of package names separated by space OR press enter to do the diff automatically.")

if input_diff:
    selective_ui_tests_with_diff(input_diff.split(" "))
else:
    selective_ui_tests()

# project_path = "..."
# path = project_path + "...."
# print(_find_all_ui_tests(path, SRC_JAVA_ANDROID_TEST_PATTERN, os.path.join(project_path)))
