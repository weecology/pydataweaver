from dataweaver.lib.scripts import SCRIPT_LIST, get_script


def datasets(keywords=None, licenses=None):
    """Return list of all available datasets."""
    script_list = SCRIPT_LIST()

    if not keywords and not licenses:
        return sorted(script_list, key=lambda s: s.name.lower())

    result_scripts = set()
    if licenses:
        licenses = [l.lower() for l in licenses]
    for script in script_list:
        if script.name:
            if licenses:
                # get a list of all licenses in lower case present in the scripts
                script_license = [lc.lower for lc in sum(script.licenses.values(), [])]

                if script_license and set(script_license).intersection(set(licenses)):
                    result_scripts.add(script)
                    continue
            if keywords:
                script_keywords = script.title + " " + script.name
                if script.keywords:
                    script_keywords = script_keywords + " " + "-".join(script.keywords)
                script_keywords = script_keywords.lower()
                for k in keywords:
                    if script_keywords.find(k.lower()) != -1:
                        result_scripts.add(script)
                        break

    return sorted(list(result_scripts), key=lambda s: s.name.lower())


def dataset_names():
    """Return list of all available dataset names."""
    all_scripts = datasets()
    scripts_name = []

    for script in all_scripts:
        scripts_name.append(script.name)

    return scripts_name


def license(dataset):
    """Get the license for a dataset."""
    return get_script(dataset).licenses


def dataset_licenses():
    """Return set with all available licenses."""
    script_license = []
    for script in SCRIPT_LIST():
        temp_list = [lc.lower for lc in sum(script.licenses.values(), [])]
        script_license.append(temp_list)
    return set(script_license)
