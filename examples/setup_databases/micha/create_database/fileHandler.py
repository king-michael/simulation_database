# coding=utf-8
"""
_info_ fileHandler
"""


def get_data_from_info_file(fname, list_comments=('#',)):
    """
    Function to get data from a `_info_` file.

    In general every file with a logic `KEY : VALUE`

    Parameters
    ----------
    fname : str
        File name.
    list_comments : List[str] or Tuple[str], optional
        List of comment characters.

    Returns
    -------
    data : dict
        Dictionary of all `(key, value)` pairs found in the given file
    """

    # Create a dict to store data in
    data={}

    with open(fname, 'r') as fp:
        for line in fp:
            line_strip = line.strip()
            if len(line_strip) == 0: continue  # empty lines
            if line_strip[0] in list_comments: continue  # comments
            line_split = line_strip.split(":", 1)  # max split 1
            if len(line_split) == 2:
                data[line_split[0].strip()] = line_split[1].strip()
    return data
