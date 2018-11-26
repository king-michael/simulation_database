from collections import namedtuple
from datetime import datetime

db_path = 'test_database.db'

attributes = ['entry_id', 'path', 'owner', 'url', 'type', 'description', 'created_on']
obj_main = namedtuple('Main_obj', attributes)
reference_dict = {
    'TEST0001' : obj_main(entry_id='TEST0001',
                          path='here/am/i',
                          owner='tester',
                          url='http://somewhere.else',
                          type='sim',
                          description='blablabla',
                          created_on=datetime(2009, 12, 20, 0, 0),),
    'TEST0003' : obj_main(entry_id='TEST0003',
                          path='here/am/i/not',
                          owner='tester',
                          url='http://somewhere.else2',
                          type='sim',
                          description='blablabla',
                          created_on=datetime(1999, 12, 13, 0, 0),),
    'TEST0002' : obj_main(entry_id='TEST0002',
                          path='\what\ever\is\here',
                          owner='tester2',
                          url=None,
                          type='awesome',
                          description='blabla',
                          created_on=None,),
}