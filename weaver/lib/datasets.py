from weaver.lib.scripts import get_script


def datasets(arg_keyword=None):
    """Return list of all available datasets."""
    all_scripts = []

    return all_scripts


def license(dataset):
    """Get the license for a dataset."""
    return get_script(dataset).licenses[0]['name']
