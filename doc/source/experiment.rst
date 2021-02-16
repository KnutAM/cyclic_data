Description of experiments
***************************

#. Add predeformation end data and refer to full data set on Mendeley
   data. Note the sign reversal! The data included should be corrected
   wrt. torsional sign
   
   * The strains after each predeformation level (PD1,3,6)
   * The Hill yield surfaces after each predeformation level (PD1,3,6)


The pearlitic rail steel R260 was predeformed using the method in 
`Meyer et al. (2018a) <https://doi.org/10.1016/j.ijsolstr.2017.10.007>`_, 
as reported in 
`Meyer et al. (2019) <https://doi.org/10.1016/J.FINEL.2019.05.006>`_
Thereafter, the bars where re-machined into tubular test bars, as 
described in  
`Meyer et al. (2020a) <https://doi.org/10.1016/j.euromechsol.2020.103977>`_. 
The definitions of stresses and strains used are 
based on the following coordinate system:

|csys|

.. table:: Definitions of experiment stress and strain variables
   :widths: auto

   ============================  ==============  ==============
   Value                         Short notation  Description
   ============================  ==============  ==============
   :math:`\sigma_{zz}`           ``sig``         Axial stress
   :math:`\sigma_{\theta z}`     ``tau``         Shear stress
   :math:`\epsilon_{zz}`         ``eps``         Axial strain
   :math:`2\epsilon_{\theta z}`  ``gam``         Shear strain
   ============================  ==============  ==============
   
The short notation is used to access the fields in the data.


Predeformation experiments
==========================
The full data for one predeformation experiment is available: 
`Predeformation of R260 rail steel <https://data.mendeley.com/datasets/sjsyw6cmfd/2>`_. 
**Note**: In that dataset, the torque, and rotations are reversed
compared to the definitions above. 
The results after different levels of predeformation (PDx) 
are given in the following table. 
In this table, the strains follow the definition given 
by the figure above. 

.. table:: Predeformation strains from 
           `Predeformation of R260 rail steel <https://data.mendeley.com/datasets/sjsyw6cmfd/2>`_ 
           at :math:`r=6.5\,\mathrm{mm}`
   :widths: auto 

   ====================     =======================  ==============================  =======================
   Predeformation level     :math:`\epsilon_{zz}^0`  :math:`2\epsilon_{\theta z}^0`  :math:`\epsilon_{rr}^0`
   ====================     =======================  ==============================  =======================
    **PD0**                                  0.00 %                          0.00 %                   0.00 %
    *PD1*                                   -6.08 %                        -20.82 %                   3.47 %
    *PD2*                                   -9.96 %                        -40.67 %                   5.61 %
    **PD3**                                -13.21 %                        -59.50 %                   7.30 %
    *PD4*                                  -16.02 %                        -77.73 %                   9.37 %
    *PD5*                                  -18.61 %                        -95.52 %                  11.32 %
    **PD6**                                -20.93 %                       -112.89 %                  12.80 %
   ====================     =======================  ==============================  =======================

Subsequent experiments have only been carried out for PD0, PD1, PD3, and PD6. 
These levels are marked in **bold**, while the remaining in *italic* to highlight this fact. 


In `Meyer et al. (2020a) <https://doi.org/10.1016/j.euromechsol.2020.103977>`_
the yield surfaces after the predeformation where calibrated. 
The Hill yield surface, :math:`\varPhi=0`, is given as

.. math::
    
    \varPhi(\sigma_{zz}, \sigma_{\theta z}) = \sqrt{
      \left(\frac{\sigma_{zz}-b_{zz}}{H_{zz,zz}}\right)^2
    + \sqrt{3} \frac{(\sigma_{zz}-b_{zz})(\sigma_{\theta z}-b_{\theta z})}{h_{zz,\theta z}}
    + 3\left(\frac{\sigma_{\theta z}-b_{\theta z}}{H_{\theta z, \theta z}}\right)^2} - 1 = 0

where :math:`H_{zz,zz},H_{\theta z, \theta z},h_{zz,\theta z},b_{zz}`, 
and :math:`b_{\theta z}` are parameters for the Hill yield surface. 

.. table:: Hill yield surface parameters for low plastic work limit from 
           `Meyer et al. (2020a) <https://doi.org/10.1016/j.euromechsol.2020.103977>`_
   :widths: auto 
   
   ===============================  ===========  ===========  ===========  ===========  =====
                         Parameter          PD0          PD1          PD3          PD6   Unit
   ===============================  ===========  ===========  ===========  ===========  =====
                    :math:`b_{zz}`          1.7        -50.6        -57.6        -30.9    MPa
              :math:`b_{\theta z}`          3.6         44.3         33.2         32.2    MPa
                 :math:`H_{zz,zz}`        335.8        341.2        373.4        401.2    MPa
    :math:`H_{\theta z, \theta z}`        365.5        287.3        292.1        313.3    MPa
           :math:`h_{zz,\theta z}`    3429072.7    -333521.0    -167544.4   -1149326.5  MPa^2
   ===============================  ===========  ===========  ===========  ===========  =====


.. table:: Hill yield surface parameters for high plastic work limit from 
           `Meyer et al. (2020a) <https://doi.org/10.1016/j.euromechsol.2020.103977>`_
   :widths: auto
   
   ===============================  ===========  ===========  ===========  ===========  =====
                         Parameter          PD0          PD1          PD3          PD6   Unit
   ===============================  ===========  ===========  ===========  ===========  =====
                    :math:`b_{zz}`         -4.1        -91.0        -93.0        -63.9    MPa
              :math:`b_{\theta z}`          2.7        111.8        104.1         89.6    MPa
                 :math:`H_{zz,zz}`        472.0        590.5        640.0        706.2    MPa
    :math:`H_{\theta z, \theta z}`        498.2        531.5        586.6        587.6    MPa
           :math:`h_{zz,\theta z}`    4690470.1   -1070440.8   -1315116.5   -8602480.0  MPa^2
   ===============================  ===========  ===========  ===========  ===========  =====



Cyclic data
============
Describe structure and fields of hdf5 data.


.. |csys| image:: /img/csys.svg
          :align: middle
          :alt: 