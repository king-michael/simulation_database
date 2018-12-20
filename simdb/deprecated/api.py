
def get_tags(db_path):
    """
    Function to get all tags used in a database.

    Parameters
    ----------
    db_path : str
        Path to the database

    Returns
    -------
    tags : Tuple[str]
        Unique tag list.
    """

    session = connect_database(db_path=db_path)
    query = session.query(distinct(Keywords.name)).select_from(Keywords).filter(Keywords.value.is_(None))
    results = query.all()
    session.close()

    return next(iter(zip(*results)), [])


def get_keywords(db_path):
    """
    Function to get all keywords with their values as list

    Parameters
    ----------
    db_path : str
        Path to the database

    Returns
    -------
    tags : dict[str, list]
        Unique keyword dictonary.
    """

    session = connect_database(db_path=db_path)
    query = session.query(Keywords.name, Keywords.value).distinct().filter(not_(Keywords.value.is_(None)))
    keywords = dict((k, list(zip(*v))[1]) for k, v in itertools.groupby(query.all(), lambda x: x[0]))
    session.close()

    return keywords


def add_tag(db_path, entry_id, tag_name):
    """
    Add tag to entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    tag_name : str
        Tag name

    Returns
    -------
    True if tag was added, otherwise False
    """

    s = connect_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    if entry:

        # tag already there
        if entry.keywords_query.filter_by(name=tag_name, value=None).first():
            print("Tag already assigned to entry")

        # tagname used for keyword
        elif entry.keywords_query.filter_by(name=tag_name).first():
            print("Tag is already used for keyword. You can't add this tag. One could say that this problem might be avoided if one would use two separate tables for tags and keywords.")

        # add tag
        else:
            tag = Keywords(name=tag_name)
            entry.keywords.append(tag)
            s.commit()
            status = True

    s.close()

    return status


def remove_tag(db_path, entry_id, tag_name):
    """
    Remove tag from entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    tag_name : str
        Tag name

    Returns
    -------
    True if tag was removed otherwise False
    """

    s = connect_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    tag = entry.keywords_query.filter_by(name=tag_name, value=None).first()
    if entry and tag:
        entry.keywords.remove(tag)
        s.commit()
        status = True

    s.close()

    return status




def add_keyword(db_path, entry_id, **kwargs):
    """
    Add keywords to entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    **kwargs : kwargs
        keyword1="value1", keyword2="value2"

    Returns
    -------
    True
    """

    s = connect_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    if entry:
        status = []
        for name, value in kwargs.items():

            # keyword is already there but might be a tag or might have a different value
            if entry.keywords_query.filter_by(name=name).first():

                # keyword is already there but a tag
                if entry.keywords_query.filter_by(name=name, value=None).first():
                    print(
                        "You are trying to assing a keyword which is already used for a tag. One could say that this problem might be avoided if one would use two separate tables for tags and keywords.")
                    status.append(False)

                # keyword is already there
                else:
                    keyword = entry.keywords_query.filter_by(name=name).first()
                    print("Keyword already there: {} = {}".format(keyword.name, keyword.value))
                    status.append(False)

            # keyword is not there
            else:
                entry.keywords.append(Keywords(name=name, value=value))
                s.commit()
                status.append(True)

        status = np.any(status)

    s.close()

    return status


def alter_keyword(db_path, entry_id, **kwargs):
    """
    Alter existing keywords of entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    **kwargs : kwargs
        keyword = "value": Alter keyword to value

    Returns
    -------
    True
    """

    s = connect_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    if entry:
        status = []
        for name, value in kwargs.items():

            # keyword is there
            keyword = entry.keywords_query.filter_by(name=name).first()
            if keyword and keyword.value is not None:

                keyword.value = value
                s.commit()
                status.append(True)

            # keyword is not there
            else:
                status.append(False)

        status = np.any(status)

    s.close()

    return status


def remove_keyword(db_path, entry_id, **kwargs):
    """
    Remove keywords from entry.

    Parameters
    ----------
    db_path : str
        Path to the database
    entry_id : str
        Entry ID in database
    **kwargs : kwargs
        keyword = "value": Keyword is given, remove if entry has given value
        keyword = None : Remove keyword independent of value

    Returns
    -------
    True
    """

    s = connect_database(db_path)
    status = False

    entry = s.query(Main).filter(Main.entry_id == entry_id).first()
    if entry:
        status = []
        for name, value in kwargs.items():

            # keyword is there
            keyword = entry.keywords_query.filter_by(name=name).first()
            if keyword:

                # keyword might be a tag
                if keyword.value is not None and (value == None or value == keyword.value):
                    entry.keywords.remove(keyword)
                    s.commit()
                    status.append(True)

            # keyword is not there
            else:
                status.append(False)

        status = np.any(status)

    s.close()

    return status


def get_entry_table(db_path, group_names=None, tags=None, columns=None):
    """Get pandas table of all entries meeting the selection creteria.
    This is maybe a better way to get entries since selection is on SQL level.

    Args:
        db_path: string, path to database
        group_names: list, names of groups, logic for groups is OR
        tags: list, logic for tags is AND
        columns: list, columns which should be displayed
    """

    # open databae
    s = connect_database(db_path)
    q = s.query(Main).options(noload(Main.keywords))

    # filter by groups
    if group_names is not None:
        groups = []
        for groupname in group_names:
            try:
                # collect groups
                groups.append(s.query(Groups).filter(Groups.name == groupname).one())
            except NoResultFound:
                print("{} is not a group in selected database.".format(groupname))

        groups = [Main.groups.any(id=group.id) for group in groups]
        q = q.filter(or_(*groups))

    # filter by tags
    if tags is not None:
        tags = [and_(Main.keywords.any(name=tag), Main.keywords.any(value=None)) for tag in tags]

        q = q.filter(and_(*tags))

    # get entries as pandas table
    df = pd.read_sql(q.statement, s.bind, index_col="id")

    s.close()

    # convert output
    if columns is not None:
        df = df[columns]

    return df


#### deprecated #####
# functions below are deprecated and will be removed
# after checking that they are not used any more
# Micha: please do not remove them. get_entry_keywords / tags could be usefull
# used in app.py !

def getEntryTable(db_path, columns=["entry_id", "path", "created_on", "added_on", "updated_on", "description"],
                  load_keys=True, load_tags=True):
    '''Get a pandas DataFrame with all entries in a data base and
    keywords and tags.'''
    s = connect_database(db_path)

    # get DB tables as pandas DataFrames
    main = pd.read_sql_table("main", s.bind)[["id"] + columns].set_index('id')
    keywords_raw = pd.read_sql_table("keywords", s.bind)

    if load_keys:
        keywords = keywords_raw[keywords_raw['value'].notna()]
        if keywords.size != 0:
            # inner join to get the connection between entries and keywords
            # m = pd.merge(main, keywords, right_on="main_id", how="inner")
            # pivot table reduces it to columns
            p = keywords.pivot(index='main_id', columns='name')["value"]
            main = pd.concat([main, p], axis=1)

    def listed(alist):
        '''Convert list to comma seperated string.'''
        return ",".join("{}".format(i) for i in alist)

    if load_tags:
        tags = keywords_raw[~keywords_raw['value'].notna()]
        if tags.notna().size != 0:
            tags = tags.drop('value', axis=1).groupby("main_id").agg({"name": listed}).rename(index=int,
                                                                                              columns={"name": "tags"})
            main = pd.concat([main, tags], axis=1)

    s.close()

    return main


def getEntryDetails(db_path, entry_id):
    s = connect_database(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()
    d = sim.__dict__
    try:
        del d["_sa_instance_state"]
    except:
        pass
    out = sim.__dict__

    s.close()
    return out


def getEntryKeywords(db_path, entry_id):
    s = connect_database(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()
    keywords = dict((k.name, k.value) for k in sim.keywords
                    if k.value != 'None' and k is not None)

    s.close()
    return keywords


def getEntryTags(db_path, entry_id):
    s = connect_database(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()
    tags = [t.name for t in sim.keywords if t.value == "None" or t.value is None]

    s.close()
    return tags


def getEntryMeta(db_path, entry_id):
    s = connect_database(db_path)

    sim = s.query(Main).filter(Main.entry_id == entry_id).one()

    out = {}
    for meta_group in sim.meta.all():
        out[meta_group.name] = {meta.name: meta.value for meta in meta_group.entries.all()}

    s.close()
    return out