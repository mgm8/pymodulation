*****
Usage
*****

This section presents examples of how to use the library for each supported modulation type.

GFSK
====

The GFSK modulation can be used through the *GFSK* class, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation.gfsk import GFSK

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

    from pymodulation.gmsk import GMSK

    mod = GMSK(0.5, 9600)   # BT = 0.5, baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits, bb_sig = mod.demodulate(fs, samples)

    print("Demodulated bits:", list(map(int, bits)))
