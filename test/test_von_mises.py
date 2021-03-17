import numpy as np
from pytest import approx

import cyclic_data.von_mises as vm


def test_vm_stress():
    # Test both for single float and np.array
    for val in [np.random.rand(), np.random.rand(10)]:
        assert vm.vm(val, 0.0) == approx(np.abs(val))
        assert vm.vm(0.0, val) == approx(np.abs(val)*np.sqrt(3))
        assert vm.vm(val, val) == approx(np.sqrt(val**2 + 3*val**2))


def test_vm_strain():
    # Test both for single float and np.array
    for val in [np.random.rand(), np.random.rand(10)]:
        assert vm.evm(val, 0.0) == approx(np.abs(val))
        assert vm.evm(0.0, val) == approx(np.abs(val)/np.sqrt(3))
        assert vm.evm(val, val) == approx(np.sqrt(val**2 + (1.0/3.0)*val**2))


def test_vm_angle():
    val = 1.1 + np.random.rand()
    assert val > 0.0    # Else test conditions are invalid -> change test
    assert np.cos(vm.vm_angle(val, 0.0)) == approx(1.0)
    assert np.sin(vm.vm_angle(0.0, val)) == approx(1.0)
    assert np.cos(vm.vm_angle(-val, 0.0)) == approx(-1.0)
    assert np.sin(vm.vm_angle(0.0, -val)) == approx(-1.0)

    # Check that interval adjustment work as expected
    sig = np.array([0.0, -1.0])
    tau = np.array([1.0, -1.0])/np.sqrt(3)
    assert vm.vm_angle(sig, tau) == approx(np.array([1./2., 5./4.])*np.pi)


def test_stress_polar():

    def rand_fun(num):
        return np.random.rand(num) if num > 1 else np.random.rand()

    for n in [1, 10]:
        sig = rand_fun(n)
        tau = rand_fun(n)
        radius, angle = vm.stress_polar(sig, tau)

        # Check that correct radius is given
        assert radius == approx(vm.vm(sig, tau))

        # Check that correct angle is given
        # (note that numerical issues can cause jump by 2pi)
        vma = vm.vm_angle(sig, tau)
        a_tol = np.pi/1.e6
        check_a = [np.abs(np.abs(vma-angle)-a) < a_tol for a in [0, 2*np.pi]]
        if n > 1:
            assert all(np.logical_xor(*check_a))
        else:
            assert np.logical_xor(*check_a)


