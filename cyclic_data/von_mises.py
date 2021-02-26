"""Module used to analyze wrt. von Mises effective stresses
"""
import numpy as np


def stress_polar(sig, tau):
    """ Calculate the polar stress coordinates in the ``sig``-sqrt(3)``tau``
    plane using the radius from :py:func:`von_mises` and the angle from
    :py:func:`vm_angle`. See respective function for input/output details

    :returns: radius and angle
    """

    radius = vm(sig, tau)
    angle = vm_angle(sig, tau)

    return radius, angle


def vm(sig, tau):
    """ Calculate the von Mises stress given a normal and shear stress

    :param sig: Axial stress, :math:`\\sigma_{zz}`
    :type sig: float, np.array

    :param tau: Shear stress, :math:`\\sigma_{\\theta z}`
    :type tau: float, np.array

    :returns: The von Mises stress
    :rtype: float, np.array
    """
    return np.sqrt(sig**2 + 3*tau**2)


def vm_angle(sig, tau):
    """ Calculate the angle in the ``sig``-``tau`` space, where ``tau`` is scaled to obtain a circle for equal
    von Mises stresses. To avoid jumps around :math:`\\pi`, the interval (width=2pi) is adjusted within [-2pi, 2pi],
    i.e. the interval is [amin, amin+2pi] where the mean angle is [amin+pi] and amin is in [-2pi,0]
    This only works as long as the angles are not rotating continuously, but remain within a certain smaller
    interval with width less than :math:`2\\pi`. In any case, the angle is measured from the ``sig``-axis.

    :param sig: Axial stress, :math:`\\sigma_{zz}`
    :type sig: float, np.array

    :param tau: Shear stress, :math:`\\sigma_{\\theta z}`
    :type tau: float, np.array

    :returns: The angle relative the sigma axis, in the :math:`\\sigma_{zz}-\\sqrt{3}\\sigma_{\\theta z}` plane
    :rtype: float, np.array
    """

    x = [sig, np.sqrt(3) * tau]
    xm = [np.mean(xi) for xi in x]
    mid_angle = np.arctan2(xm[1], xm[0])
    xp = [x[0]*np.cos(mid_angle) + x[1]*np.sin(mid_angle),
          -x[0]*np.sin(mid_angle) + x[1]*np.cos(mid_angle)]

    angles = np.arctan2(xp[1], xp[0]) + mid_angle

    return angles


def evm(eps, gam):
    """ Calculate the effective von Mises strain given an axial strain and a shear strain

    :param eps: Axial strain, e.g. :math:`\\epsilon_{zz}`
    :type eps: float, np.array

    :param gam: Shear strain, e.g. :math:`2\\epsilon_{\\theta z}`
    :type gam: float, np.array

    :returns: The von Mises strain
    :rtype: float, np.array
    """
    return np.sqrt(eps**2 + gam**2/3)
