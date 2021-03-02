import os, shutil
import numpy as np
from cyclic_data.io import Hdf5Write, Hdf5Read

hdf5_test_file = os.path.join(os.path.dirname(__file__), 'test_file.hdf5')


def make_example_file(name, define_custom=False):
    # Common for all test bars
    cols_dict = {'time': 0, 'acnt': 1, 'forc': 2, 'astr': 3, 'disp': 4,
                 'tcnt': 5, 'torq': 6, 'tstr': 7, 'rota': 8}
    cols_dtype = {'acnt': np.uint32, 'tcnt': np.uint32}
    cols_descr = {'time': 'alternative time description'}
    if define_custom:
        hdf = Hdf5Write(name, cols_dict, cols_dtype=cols_dtype, cols_descr=cols_descr)
    else:
        hdf = Hdf5Write(name, cols_dict)

    data = np.zeros((100, 9))   # Dummy data to add
    attrs = {'inner_diameter': 12.0, 'outer_diameter': 14.0, 'gauge_length': 2.0,
             'concentricity': 0.01, 'load_angle': 0, 'load_type': 'Proportional', 'pdef_level': 0}
    # Add 3 test bars with different attributes
    hdf.add_bar(data, 'T01', attrs)
    attrs['pdef_level'] = 1
    hdf.add_bar(data, 'T02', attrs)
    attrs['load_type'] = 'non-proportional'
    hdf.add_bar(data, 'T03', attrs)

    # Close the hdf object in the end
    hdf.close()


def test_write():
    fname = 'tmp_test.hdf5'
    make_example_file(fname)
    assert os.path.exists(fname)
    # Overwrite, and use custom definitions
    make_example_file(fname, define_custom=True)
    assert os.path.exists(fname)
    os.remove(fname)
    # Write without fewer cols_dict than required, those columns get zero data by default
    hdf = Hdf5Write(fname, {'time': 0})
    try:
        hdf.add_bar(np.zeros((2, 2)), 'tmp', {'inner_diameter': 10, 'outer_diameter': 12})
        raise Exception('')
    except ValueError:
        pass
    except Exception as e:
        assert False, 'gauge_diameter attribute missing, should raise ValueError. Printed ' + str(e)

    hdf.close()
    os.remove(fname)


def test_read():
    """ Verify that the Hdf5Data class can initialize correctly by opening the test file
        This test isolates that the test file used to verify other functionalities is working
    """
    # Generate the test file
    hdf5_test_file = 'tmp_test_file.hdf5'
    make_example_file(hdf5_test_file)

    # Verify that we can open and close the file
    try:
        hdf = Hdf5Read(hdf5_test_file)
    except Exception as e:
        assert False, "opening test file raised " + str(e)
    
    assert isinstance(hdf, Hdf5Read)   # Ensure that instance exists
    assert hdf.is_open()               # Ensure that file is open
    
    hdf.close()
    assert not hdf.is_open()           # Ensure that file is closed

    # Test getting by group
    existing_group = 'T01'
    hdf = Hdf5Read(hdf5_test_file)
    data, attr = hdf.get_data_by_group(existing_group)
    assert isinstance(data, dict)
    assert 'time' in data
    assert isinstance(data['time'], np.ndarray)
    assert isinstance(attr, dict)
    assert 'load_angle' in attr
    assert 'group' not in attr, '"group" should not be in attributes when returned from get_by_group'

    non_existing_group = 'non_existing'
    data, attr = hdf.get_data_by_group(non_existing_group)
    assert data is None
    assert attr is None

    # Test getting by attributes
    #  Test that function fails for an attribute not in the data
    def verify_failure():
        attr = {'load_angle': 0, 'non_existing_attr': ''}
        try:
            hdf.get_data_by_attributes(attr)
            print('Should exit with error if a non-existing attribute is requested')
            return False
        except KeyError:  # Should fail with KeyError if attribute not found in file
            return True
        except Exception as e:
            print('Should give KeyError for non-existing attribute, but the following was thrown:')
            print(e.__class__)
            print(e)
            return False

    assert verify_failure()

    # Test that a list is returned
    # Test that the list has length 2 if 2 attributes match
    attr = {'load_angle': 0, 'load_type': 'Proportional'}
    data, attr = hdf.get_data_by_attributes(attr)
    assert isinstance(data, list)
    assert isinstance(attr, list)
    assert len(data) == len(attr)
    assert len(data) == 2

    # Test that the list is empty if no attributes match
    attr = {'load_angle': 0, 'load_type': 'does_not_exist'}
    data, attr = hdf.get_data_by_attributes(attr)
    assert len(data) == 0
    assert len(attr) == 0


    # Test generation of html table
    attrs = ['load_type', 'load_angle', 'pdef_level', 'outer_diameter', 'inner_diameter', 'concentricity']
    formats = ['s', '05.1f', '0.0f', '6.3f', '6.3f', '5.3f']
    hdf.make_html_table(attrs, formats, output_dir='tmp_table')
    # Ensure that table folder created
    assert os.path.exists('tmp_table')
    # Assert that files have been created
    assert os.path.exists('tmp_table/test_data.html')
    assert os.path.exists('tmp_table/style.css')
    assert os.path.exists('tmp_table/table.js')

    # Compare with reference solution
    ref_file = os.path.join(os.path.dirname(__file__), 'reference_table.html')
    with open(ref_file, 'r') as fid:
        reference = fid.read()

    with open('tmp_table/test_data.html', 'r') as fid:
        created = fid.read()
    # Check that content match. If not, then a manual check that the rendered output is ok should be done.
    # If this looks good, the reference solution can be updated if desired
    assert reference == created, ('Check that html rendering of tmp_table/test_data.html is ok. '
                                  + 'If changes to html expected and result good, ok to update reference.')

    # Ensure that we can overwrite and not specify formats
    hdf.make_html_table(attrs, output_dir='tmp_table')

    shutil.rmtree('tmp_table')
    hdf.close()
    os.remove(hdf5_test_file)
