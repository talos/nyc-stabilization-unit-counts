from download_direct import main

def test_download_one_bill():
    '''
    Confirm we can download a bill without throwing an error.
    '''
    main('20150605', 'SOA', '3', '1772', '74')
