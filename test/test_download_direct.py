import os
from download_direct import main

def test_download_one_bill():
    '''
    Confirm we can download a bill without throwing an error.
    '''
    assert main('20170602', 'SOA', '3', '1772', '74') == 0
    assert os.path.exists('./data/3/01772/0074/June 2, 2017 - Quarterly Property Tax Bill.pdf')
