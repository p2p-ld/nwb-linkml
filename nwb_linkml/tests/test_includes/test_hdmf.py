import pytest
from typing import Tuple
import numpy as np

from nwb_linkml.models.pydantic.core.v2_7_0.namespace import ElectricalSeries, NWBFileGeneralExtracellularEphysElectrodes

@pytest.fixture()
def electrical_series() -> Tuple[ElectricalSeries, NWBFileGeneralExtracellularEphysElectrodes]:
    """
    Demo electrical series with adjoining electrodes
    """
    n_electrodes = 5
    n_times = 100
    data = np.arange(0, n_electrodes*n_times).reshape(n_times, n_electrodes)
    timestamps = np.linspace(0, 1, n_times)

    # make electrodes tables
    electrodes = NWBFileGeneralExtracellularEphysElectrodes(
        id = np.arange(0, n_electrodes),
        x = np.arange(0, n_electrodes),
        y = np.arange(n_electrodes, n_electrodes*2)
    )