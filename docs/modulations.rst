.. modulations.rst

   Copyright The PyModulation Contributors.

   PyModulation Documentation

   This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
   International License. To view a copy of this license,
   visit http://creativecommons.org/licenses/by-sa/4.0/.

***********
Modulations
***********

BPSK
====

Binary Phase Shift Keying (BPSK) is one of the simplest and most robust digital modulation schemes used in wireless and satellite communications. In BPSK, digital information is transmitted by changing the phase of a carrier signal between two possible states separated by 180 degrees. Typically, a binary `0` is represented by a carrier phase of 0°, while a binary `1` is represented by a phase of 180°.

The BPSK signal can be expressed as:

.. math::

   s(t) = A \cos(2\pi f_c t + \phi)

where:

* :math:`A` is the signal amplitude;
* :math:`f_c` is the carrier frequency;
* :math:`\phi` is the carrier phase, taking values of 0 or :math:`\pi` radians according to the transmitted bit.

BPSK offers excellent noise immunity and achieves a low bit error rate (BER) for a given signal-to-noise ratio (SNR). Its simplicity allows for straightforward implementation in both transmitters and receivers. However, since each symbol conveys only one bit of information, BPSK has lower spectral efficiency than higher-order modulation schemes such as QPSK and QAM.

Due to its robustness and implementation simplicity, BPSK is widely employed in satellite telemetry and telecommand links, deep-space communications, navigation systems, and other applications requiring reliable data transmission under challenging channel conditions.

GFSK
====

Gaussian Frequency Shift Keying (GFSK) is a modulation technique derived from Frequency Shift Keying (FSK), where digital data is transmitted by shifting the carrier frequency between discrete values. Unlike traditional FSK, GFSK applies a Gaussian filter to the baseband pulses before modulation, which smooths the phase transitions and reduces spectral bandwidth. This filtering minimizes abrupt frequency changes, resulting in a more compact power spectrum and reduced interference with adjacent channels. GFSK is particularly advantageous in wireless communication systems where efficient bandwidth utilization and low power consumption are critical.  

One of the most notable applications of GFSK is in Bluetooth technology, where it is used for its robustness and spectral efficiency. The Gaussian filtering helps mitigate intersymbol interference (ISI) and improves performance in noisy environments. Additionally, GFSK supports both coherent and non-coherent detection, offering flexibility in receiver design. Its constant envelope property ensures efficient power amplifier operation, making it suitable for battery-powered devices. Overall, GFSK strikes a balance between simplicity, spectral efficiency, and reliability, making it a popular choice for short-range wireless communication systems.

GMSK
====

Gaussian Minimum Shift Keying (GMSK) is a continuous-phase modulation scheme derived from Frequency Shift Keying (FSK), where the digital signal is filtered using a Gaussian filter before modulation. This filtering smooths the phase transitions, resulting in a nearly constant envelope and significantly reduced spectral sidelobes compared to traditional FSK. The key feature of GMSK is its ability to achieve high spectral efficiency while maintaining low out-of-band emissions, making it ideal for bandwidth-constrained wireless systems.  

A notable application of GMSK is in the Global System for Mobile Communications (GSM), where it was chosen for its robustness against interference and efficient use of available spectrum. The modulation's constant envelope allows for the use of highly efficient nonlinear power amplifiers, reducing power consumption in mobile devices. Additionally, GMSK's resistance to multipath fading and phase noise enhances performance in challenging radio environments. Despite its slightly higher complexity in demodulation compared to simpler FSK schemes, GMSK remains a widely adopted modulation technique due to its excellent balance between spectral efficiency, power efficiency, and reliability in wireless communication systems.
