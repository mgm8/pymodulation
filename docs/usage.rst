.. usage.rst

   Copyright The PyModulation Contributors.

   PyModulation Documentation

   This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
   International License. To view a copy of this license,
   visit http://creativecommons.org/licenses/by-sa/4.0/.

*****
Usage
*****

This section presents examples of how to use the library for each supported modulation type.

ASK
===

The ASK modulation can be used through the *ASK* class, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation import ASK

    mod = ASK(4, 9600)    # Order = 4, Baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

The *modulate* method returns the IQ samples of the generated signal, the corresponding sampling rate, and the signal duration in seconds. The *demodulate* method allows the demodulation of a ASK signal, taking the corresponding IQ samples as input, and producing as output the data bitstream contained in the signal and the baseband signal samples (in NRZ format).

OOK
***

For OOK, the usage is very similar to ASK, but with the difference that there is no need to define the order of the modulation (as expected for OOK, it is fixed as 2):

.. code-block:: python

    from pymodulation import OOK

    mod = OOK(9600)    # Baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

BPSK
====

The BPSK modulation can be used through the *BPSK* class, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation import BPSK

    mod = BPSK(9600)    # Baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

The *modulate* method returns the IQ samples of the generated signal, the corresponding sampling rate, and the signal duration in seconds. The *demodulate* method allows the demodulation of a BPSK signal, taking the corresponding IQ samples as input, and producing as output the data bitstream contained in the signal and the baseband signal samples (in NRZ format).

GFSK
====

The GFSK modulation can be used through the *GFSK* class, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation import GFSK

    mod = GFSK(2.5, 0.5, 9600)  # Modulation index = 2.5, BT = 0.5, Baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits, bb_sig = mod.demodulate(fs, samples)

    print("Demodulated bits:", list(map(int, bits)))

The *modulate* method returns the IQ samples of the generated signal, the corresponding sampling rate, and the signal duration in seconds. The *demodulate* method allows the demodulation of a GFSK signal, taking the corresponding IQ samples and sampling rate as input, and producing as output the data bitstream contained in the signal and the baseband signal samples (in NRZ format).

GMSK
====

This modulation can be used in a manner almost identical to GFSK modulation, with the difference that in this case the modulation index is fixed at 0.5, as expected for this type of modulation. An example of usage can be seen in the code below.

.. code-block:: python

    from pymodulation import GMSK

    mod = GMSK(0.5, 9600)   # BT = 0.5, baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits, bb_sig = mod.demodulate(fs, samples)

    print("Demodulated bits:", list(map(int, bits)))

QPSK
====

The QPSK modulation can be used through the *QPSK* class, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation import QPSK

    mod = QPSK(9600)    # Baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

The *modulate* method returns the IQ samples of the generated signal, the corresponding sampling rate, and the signal duration in seconds. The *demodulate* method allows the demodulation of a QPSK signal, taking the corresponding IQ samples as input, and producing as output the data bitstream contained in the signal and the baseband signal samples (in NRZ format).
