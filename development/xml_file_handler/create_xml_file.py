import sys
from lxml import etree
from datetime import datetime

if sys.version_info.major > 2:
    basestring = str




def create_xmlfile(file, dict_sim, nested=True):
    """
    Function to create an XML file from a dict.
    The dict structure is releated to the databaseModel.

    Stored Items
    ------------
    `['entry_id', 'path', 'owner', 'url', 'type', 'description', 'created_on', 'deleted', 'archived']`



    Parameters
    ----------
    file
    dict_sim
    nested

    Returns
    -------

    """
    stored_keys_main = ['entry_id', 'path',
                        'owner', 'url',
                        'type', 'description',
                        'created_on',
                        'deleted', 'archived']


    root = etree.Element("simdb", created_on=datetime.strftime(datetime.now(),'%Y-%m-%d'))

    # add main entries
    if any([k in stored_keys_main for k in dict_sim.keys()]):
        main = etree.SubElement(root, "main") if nested else root
        for k in stored_keys_main:
            if k in dict_sim.keys():
                etree.SubElement(main, k, value=str(dict_sim[k]))

    if 'keywords' in dict_sim:
        main = etree.SubElement(root, "keywords") if nested else root
        keywords = dict_sim.get('keywords')
        for k in sorted(keywords.keys()):
            etree.SubElement(main, 'keyword',name=k, value=str(keywords[k]))

    if 'metagroups' in dict_sim:
        main = etree.SubElement(root, "metagroups") if nested else root
        metagroups = dict_sim.get('metagroups')
        for k in sorted(metagroups.keys()):
            metagroup = etree.SubElement(main, 'metagroup', name=k)
            for j,v in metagroups[k].items():
                etree.SubElement(metagroup, 'metaentry', name=j, value=str(v))

    if 'groups' in dict_sim:
        main = etree.SubElement(root, "groups") if nested else root
        for group_id, name in dict_sim.get('groups').items():
            etree.SubElement(main, 'group', id=str(group_id), name=str(name))

    if 'children' in dict_sim:
        main = etree.SubElement(root, "children") if nested else root
        for child in dict_sim.get('children'):
            if isinstance(child, (tuple, list)):
                etree.SubElement(main, 'child', entry_id=str(child[0]), relation=str(child[1]))
            else:
                etree.SubElement(main, 'child', entry_id=str(child))

    if 'parents' in dict_sim:
        main = etree.SubElement(root, "parents") if nested else root
        for parent in dict_sim.get('parents'):
            if isinstance(parent, (tuple, list)):
                etree.SubElement(main, 'parent', entry_id=str(parent[0]), relation=str(parent[1]))
            else:
                etree.SubElement(main, 'parent', entry_id=str(parent))

    tree = etree.ElementTree(root)
    tree.write(file, pretty_print=True)

if __name__ == '__main__':
    dict_test = dict(
        entry_id="MK0001",
        path='/home/test/where/are/you',
        owner='me',
        url=None,
        type='GROMACS',
        description='This is more then a test.' + \
                    ' This is a really really long and stupid line.' + \
                    'Do we need a longer line?',
        created_on='datetime.now',
        deleted=True,
        archived=True,
        keywords={
            'a': 1,
            'b': 2,
            'c': 3
        },
        metagroups=dict(
            thermostat=dict(
                Tstart=300,
                Tend=9000,
                relax=100,
            ),
            barostat=dict(
                pstart=1,
                pend=2,
                relax=1000,
            )
        ),
        groups={
            1: "Awesome",
            2: 'shit'
        },
        children=[
            'MK000101',
            ('MK000102', 'subsimulation')
        ],
        parents=[
            'Overview: 1'
        ]
    )

    create_xmlfile(file='nested.xml', dict_sim=dict_test, nested=True)
    create_xmlfile(file='flat.xml', dict_sim=dict_test, nested=False)
