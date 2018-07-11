# -*- coding: utf-8 -*-
"""
Driver for the Keithley instruments

@author: pierre-francois.duc@netplus.ch
"""
import numpy as np

from .instruments import Instrument, INTF_PROLOGIX


def fake_iv_relation(
    src_type,
    src_val,
    Voc=20.5,
    Isc=3.45,
    C1=0.000002694,
    C2=0.077976842
):
    """model of solar cell IV curve
    source: https://www.sciencedirect.com/science/article/pii/S1658365512600120

    src_type should be either 'I' or 'V'
    """
    # Make sure the format is a numpy array
    src_val = np.append(np.array([]), src_val)
    # Prepare an answer based on the size of the input
    answer = np.zeros(np.size(src_val))

    if src_type == 'I':
        # Values of the input smaller than the short circuit current
        idx_ok = np.where(src_val < Isc)
        answer[idx_ok] = C2 * Voc \
            * np.log(1 + (1 - src_val[idx_ok] / Isc) / C1)
        return answer
    elif src_type == 'V':
        # Values of the input smaller than the open circuit voltage
        idx_ok = np.where(src_val < Voc)
        answer[idx_ok] = (1 - C1 * (np.exp(src_val[idx_ok] / (C2 * Voc)) - 1))\
            * Isc
        return answer


INTERFACE = INTF_PROLOGIX


class KT2400(Instrument):

    def __init__(self,
                 instr_port_name,
                 mock_mode=False,
                 instr_user_name='KT 2400',
                 **kwargs):

        # manage the presence of the keyword interface which will determine
        # which method of communication protocol this instrument will use
        if 'interface' in kwargs.keys():

            interface = kwargs.pop('interface')

        else:

            interface = INTERFACE

        instr_mesurands = {'V': 'V', 'I': 'A'}

        super(KT2400, self).__init__(instr_port_name,
                                     instr_id_name='KT2400',
                                     instr_user_name=instr_user_name,
                                     mock_mode=mock_mode,
                                     instr_intf=interface,
                                     instr_mesurands=instr_mesurands,
                                     **kwargs)

    def measure(self, channel):
        if channel in self.last_measure:

            if channel == 'V':
                if not self.mock_mode:
                    # 0 #this is to be defined for record sweep
                    self.write('VOLT:RANG:AUTO ON')
                    answer = self.ask(':READ?')
                    answer = float(answer.split(',')[0])
                else:
                    answer = np.random.random()
                self.last_measure[channel] = answer

            elif channel == 'I':
                if not self.mock_mode:
                    # 0 #this is to be defined for record sweep
                    self.write('CURR:RANG:AUTO ON')
                    answer = self.ask(':READ?')
                    answer = float(answer.split(',')[1])
                else:
                    answer = np.random.random()
                self.last_measure[channel] = answer

        else:
            print(
                "you are trying to measure a non existent channel : "
                + channel
            )
            print("existing channels :", self.channels)
            answer = None
        return answer

    def measure_voltage(self):
        return self.measure('V')

    def measure_current(self):
        return self.measure('I')

    def configure_voltage_source(self):
        if not self.mock_mode:
            self.write(':SOUR:FUNC:MODE VOLT')

    def configure_current_source(self):
        if not self.mock_mode:
            self.write(':SOUR:FUNC:MODE CURR')

    def set_voltage(self, volt_val):
        if not self.mock_mode:
            self.write(':SOUR:FUNC VOLT;:SOUR:VOLT %f' % volt_val)

    def set_current(self, curr_val):
        if not self.mock_mode:
            self.write(':SOUR:FUNC CURR;:SOUR:CURR %f' % curr_val)

    def enable_output(self):
        if not self.mock_mode:
            self.write(':OUTP ON;')

    def disable_output(self):
        if not self.mock_mode:
            self.write(':OUTP OFF;')

    def source_and_measure(self, src_type, src_val):
        """"set the given source and measure the corresponding measurand
            voltage => current
            current => voltage
        """
        if not self.mock_mode:
            if src_type == 'V':
                self.set_voltage(src_val)
                answer = self.measure_current()
            elif src_type == 'I':
                self.set_current(src_val)
                answer = self.measure_voltage()
            else:
                print("The source type should be either 'I' or 'V'")
                answer = np.nan
        else:
            answer = np.round(np.squeeze(fake_iv_relation(src_type, src_val)), 4)

        return answer

    def configure_output(
            self,
            source_mode='VOLT',
            output_level=0,
            compliance_level=0.001
    ):
        if not self.mock_mode:
            # source_mode: VOLT, CURR
            # output_level: in Volts or Amps
            # compliance level: in Amps or Vol
            if source_mode == 'CURR':
                protection = 'VOLT'
            else:
                protection = 'CURR'

            s = ':SOUR:FUNC %s;:SOUR:%s %f;:%s:PROT %r;' % (
                source_mode,
                source_mode,
                output_level,
                protection,
                compliance_level
            )
            self.write(s)
