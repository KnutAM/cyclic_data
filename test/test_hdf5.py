import os, shutil
import numpy as np
from cyclic_data.io import Hdf5Read

hdf5_test_file = os.path.join(os.path.dirname(__file__), 'test_file.hdf5')


def test_test_file():
    """ Verify that the Hdf5Data class can initialize correctly by opening the test file
        This test isolates that the test file used to verify other functionalities is working
    """
    try:
        hdf5 = Hdf5Read(hdf5_test_file)
    except Exception as e:
        assert False, "opening test file raised " + str(e)
    
    assert isinstance(hdf5, Hdf5Read)   # Ensure that instance exists
    assert hdf5.is_open()               # Ensure that file is open
    
    hdf5.close()
    assert not hdf5.is_open()           # Ensure that file is closed


def test_get_data_by_group():
    existing_group = 'T01'
    hdf5 = Hdf5Read(hdf5_test_file)
    data, attr = hdf5.get_data_by_group(existing_group)
    assert isinstance(data, dict)
    assert 'time' in data
    assert isinstance(data['time'], np.ndarray)
    assert isinstance(attr, dict)
    assert 'load_angle' in attr
    assert 'group' not in attr, '"group" should not be in attributes when returned from get_by_group'

    non_existing_group = 'non_existing'
    data, attr = hdf5.get_data_by_group(non_existing_group)
    assert data is None
    assert attr is None


def test_get_data_by_attributes():
    hdf5 = Hdf5Read(hdf5_test_file)

    # Test that function fails for an attribute not in the data
    def verify_failure():
        attr = {'load_angle': 0, 'non_existing_attr': ''}
        try:
            hdf5.get_data_by_attributes(attr)
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
    data, attr = hdf5.get_data_by_attributes(attr)
    assert isinstance(data, list)
    assert isinstance(attr, list)
    assert len(data) == len(attr)
    assert len(data) == 2

    # Test that the list is empty if no attributes match
    attr = {'load_angle': 0, 'load_type': 'does_not_exist'}
    data, attr = hdf5.get_data_by_attributes(attr)
    assert len(data) == 0
    assert len(attr) == 0


def test_html_table():
    hdf = Hdf5Read(hdf5_test_file)

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

    shutil.rmtree('tmp_table')
