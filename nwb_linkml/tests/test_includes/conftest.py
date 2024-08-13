from typing import Tuple

import numpy as np
import pytest

from nwb_linkml.models import (
    ElectricalSeries,
    ExtracellularEphysElectrodes,
    Device,
    ElectrodeGroup,
    DynamicTableRegion,
    Units,
    IntracellularElectrode,
    IntracellularElectrodesTable,
    IntracellularResponsesTable,
    IntracellularStimuliTable,
    IntracellularRecordingsTable,
)


@pytest.fixture()
def electrical_series() -> Tuple["ElectricalSeries", "ExtracellularEphysElectrodes"]:
    """
    Demo electrical series with adjoining electrodes
    """
    n_electrodes = 5
    n_times = 100
    data = np.arange(0, n_electrodes * n_times).reshape(n_times, n_electrodes).astype(float)
    timestamps = np.linspace(0, 1, n_times)

    device = Device(name="my electrode")

    # electrode group is the physical description of the electrodes
    electrode_group = ElectrodeGroup(
        name="GroupA",
        device=device,
        description="an electrode group",
        location="you know where it is",
    )

    # make electrodes tables
    electrodes = ExtracellularEphysElectrodes(
        description="idk these are also electrodes",
        id=np.arange(0, n_electrodes),
        x=np.arange(0, n_electrodes).astype(float),
        y=np.arange(n_electrodes, n_electrodes * 2).astype(float),
        group=[electrode_group] * n_electrodes,
        group_name=[electrode_group.name] * n_electrodes,
        location=[str(i) for i in range(n_electrodes)],
        extra_column=["sup"] * n_electrodes,
    )

    electrical_series = ElectricalSeries(
        name="my recording!",
        electrodes=DynamicTableRegion(
            table=electrodes,
            value=np.arange(n_electrodes - 1, -1, step=-1),
            name="electrodes",
            description="hey",
        ),
        timestamps=timestamps,
        data=data,
    )
    return electrical_series, electrodes


def _ragged_array(n_units: int) -> tuple[list[np.ndarray], np.ndarray]:
    generator = np.random.default_rng()
    spike_times = [
        np.full(shape=generator.integers(10, 50), fill_value=i, dtype=float) for i in range(n_units)
    ]
    spike_idx = []
    for i in range(n_units):
        if i == 0:
            spike_idx.append(len(spike_times[0]))
        else:
            spike_idx.append(len(spike_times[i]) + spike_idx[i - 1])
    spike_idx = np.array(spike_idx)
    return spike_times, spike_idx


@pytest.fixture(params=[True, False])
def units(request) -> Tuple[Units, list[np.ndarray], np.ndarray]:
    """
    Test case for units

    Parameterized by extra_column because pandas likes to pivot dataframes
    to long when there is only one column and it's not len() == 1
    """
    spike_times, spike_idx = _ragged_array(24)

    spike_times_flat = np.concatenate(spike_times)

    kwargs = {
        "description": "units!!!!",
        "spike_times": spike_times_flat,
        "spike_times_index": spike_idx,
    }
    if request.param:
        kwargs["extra_column"] = ["hey!"] * 24
    units = Units(**kwargs)
    return units, spike_times, spike_idx


@pytest.fixture()
def intracellular_recordings_table() -> IntracellularRecordingsTable:
    n_recordings = 10
    device = Device(name="my device")
    electrode = IntracellularElectrode(
        name="my_electrode", description="an electrode", device=device
    )
    electrodes = IntracellularElectrodesTable(
        name="intracellular_electrodes", electrode=[electrode] * n_recordings
    )
    stimuli = IntracellularStimuliTable(
        name="intracellular_stimuli",
    )
    responses = IntracellularResponsesTable()

    recordings_table = IntracellularRecordingsTable()
