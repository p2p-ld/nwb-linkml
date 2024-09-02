from datetime import datetime
from itertools import product
from pathlib import Path

import numpy as np
import pytest
from hdmf.common import DynamicTable, VectorData
from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from pynwb.base import TimeSeriesReference, TimeSeriesReferenceVectorData
from pynwb.behavior import Position, SpatialSeries
from pynwb.ecephys import LFP, ElectricalSeries
from pynwb.file import Subject
from pynwb.icephys import VoltageClampSeries, VoltageClampStimulusSeries
from pynwb.image import ImageSeries
from pynwb.ophys import (
    CorrectedImageStack,
    Fluorescence,
    ImageSegmentation,
    MotionCorrection,
    OnePhotonSeries,
    OpticalChannel,
    RoiResponseSeries,
    TwoPhotonSeries,
)


@pytest.fixture(scope="session")
def nwb_file_base() -> NWBFile:
    nwbfile = NWBFile(
        session_description="All that you touch, you change.",  # required
        identifier="1111-1111-1111-1111",  # required
        session_start_time=datetime(year=2024, month=1, day=1),  # required
        session_id="session_1234",  # optional
        experimenter=[
            "Lauren Oya Olamina",
        ],  # optional
        institution="Earthseed Research Institute",  # optional
        experiment_description="All that you change, changes you.",  # optional
        keywords=["behavior", "belief"],  # optional
        related_publications="doi:10.1016/j.neuron.2016.12.011",  # optional
    )
    subject = Subject(
        subject_id="001",
        age="P90D",
        description="mouse 5",
        species="Mus musculus",
        sex="M",
    )
    nwbfile.subject = subject
    return nwbfile


def _nwb_timeseries(nwbfile: NWBFile) -> NWBFile:
    data = np.arange(100, 200, 10)
    timestamps = np.arange(10.0)
    time_series_with_timestamps = TimeSeries(
        name="test_timeseries",
        description="an example time series",
        data=data,
        unit="m",
        timestamps=timestamps,
    )
    nwbfile.add_acquisition(time_series_with_timestamps)
    return nwbfile


def _nwb_position(nwbfile: NWBFile) -> NWBFile:
    position_data = np.array([np.linspace(0, 10, 50), np.linspace(0, 8, 50)]).T
    position_timestamps = np.linspace(0, 50).astype(float) / 200

    spatial_series_obj = SpatialSeries(
        name="SpatialSeries",
        description="(x,y) position in open field",
        data=position_data,
        timestamps=position_timestamps,
        reference_frame="(0,0) is bottom left corner",
    )
    # name is set to "Position" by default
    position_obj = Position(spatial_series=spatial_series_obj)
    behavior_module = nwbfile.create_processing_module(
        name="behavior", description="processed behavioral data"
    )
    behavior_module.add(position_obj)

    nwbfile.add_trial_column(
        name="correct",
        description="whether the trial was correct",
    )
    nwbfile.add_trial(start_time=1.0, stop_time=5.0, correct=True)
    nwbfile.add_trial(start_time=6.0, stop_time=10.0, correct=False)
    return nwbfile


def _nwb_ecephys(nwbfile: NWBFile) -> NWBFile:
    """
    Extracellular Ephys
    https://pynwb.readthedocs.io/en/latest/tutorials/domain/ecephys.html
    """
    generator = np.random.default_rng()
    device = nwbfile.create_device(name="array", description="old reliable", manufacturer="diy")
    nwbfile.add_electrode_column(name="label", description="label of electrode")

    nshanks = 4
    nchannels_per_shank = 3
    electrode_counter = 0

    for ishank in range(nshanks):
        # create an electrode group for this shank
        electrode_group = nwbfile.create_electrode_group(
            name=f"shank{ishank}",
            description=f"electrode group for shank {ishank}",
            device=device,
            location="brain area",
        )
        # add electrodes to the electrode table
        for ielec in range(nchannels_per_shank):
            nwbfile.add_electrode(
                group=electrode_group,
                label=f"shank{ishank}elec{ielec}",
                location="brain area",
            )
            electrode_counter += 1
    all_table_region = nwbfile.create_electrode_table_region(
        region=list(range(electrode_counter)),  # reference row indices 0 to N-1
        description="all electrodes",
    )
    raw_data = generator.standard_normal((50, 12))
    raw_electrical_series = ElectricalSeries(
        name="ElectricalSeries",
        description="Raw acquisition traces",
        data=raw_data,
        electrodes=all_table_region,
        starting_time=0.0,
        # timestamp of the first sample in seconds relative to the session start time
        rate=20000.0,  # in Hz
    )
    nwbfile.add_acquisition(raw_electrical_series)

    # --------------------------------------------------
    # LFP
    # --------------------------------------------------
    generator = np.random.default_rng()
    lfp_data = generator.standard_normal((50, 12))
    lfp_electrical_series = ElectricalSeries(
        name="ElectricalSeries",
        description="LFP data",
        data=lfp_data,
        electrodes=all_table_region,
        starting_time=0.0,
        rate=200.0,
    )
    lfp = LFP(electrical_series=lfp_electrical_series)
    ecephys_module = nwbfile.create_processing_module(
        name="ecephys", description="processed extracellular electrophysiology data"
    )
    ecephys_module.add(lfp)

    return nwbfile


def _nwb_units(nwbfile: NWBFile) -> NWBFile:
    generator = np.random.default_rng()
    # Spike Times
    nwbfile.add_unit_column(name="quality", description="sorting quality")
    firing_rate = 20
    n_units = 10
    res = 1000
    duration = 20
    for _ in range(n_units):
        spike_times = np.where(generator.random(res * duration) < (firing_rate / res))[0] / res
        nwbfile.add_unit(spike_times=spike_times, quality="good")
    return nwbfile


def _nwb_icephys(nwbfile: NWBFile) -> NWBFile:
    device = nwbfile.create_device(name="Heka ITC-1600")
    electrode = nwbfile.create_icephys_electrode(
        name="elec0", description="a mock intracellular electrode", device=device
    )
    stimulus = VoltageClampStimulusSeries(
        name="ccss",
        data=[1, 2, 3, 4, 5],
        starting_time=123.6,
        rate=10e3,
        electrode=electrode,
        gain=0.02,
        sweep_number=np.uint64(15),
    )

    # Create and icephys response
    response = VoltageClampSeries(
        name="vcs",
        data=[0.1, 0.2, 0.3, 0.4, 0.5],
        conversion=1e-12,
        resolution=np.nan,
        starting_time=123.6,
        rate=20e3,
        electrode=electrode,
        gain=0.02,
        capacitance_slow=100e-12,
        resistance_comp_correction=70.0,
        sweep_number=np.uint64(15),
    )
    # we can also add stimulus template data as follows
    rowindex = nwbfile.add_intracellular_recording(
        electrode=electrode, stimulus=stimulus, response=response, id=10
    )

    rowindex2 = nwbfile.add_intracellular_recording(
        electrode=electrode,
        stimulus=stimulus,
        stimulus_start_index=1,
        stimulus_index_count=3,
        response=response,
        response_start_index=2,
        response_index_count=3,
        id=11,
    )
    rowindex3 = nwbfile.add_intracellular_recording(electrode=electrode, response=response, id=12)

    nwbfile.intracellular_recordings.add_column(
        name="recording_tag",
        data=["A1", "A2", "A3"],
        description="String with a recording tag",
    )
    location_column = VectorData(
        name="location",
        data=["Mordor", "Gondor", "Rohan"],
        description="Recording location in Middle Earth",
    )

    lab_category = DynamicTable(
        name="recording_lab_data",
        description="category table for lab-specific recording metadata",
        colnames=[
            "location",
        ],
        columns=[
            location_column,
        ],
    )
    # Add the table as a new category to our intracellular_recordings
    nwbfile.intracellular_recordings.add_category(category=lab_category)
    nwbfile.intracellular_recordings.add_column(
        name="voltage_threshold",
        data=[0.1, 0.12, 0.13],
        description="Just an example column on the electrodes category table",
        category="electrodes",
    )
    stimulus_template = VoltageClampStimulusSeries(
        name="ccst",
        data=[0, 1, 2, 3, 4],
        starting_time=0.0,
        rate=10e3,
        electrode=electrode,
        gain=0.02,
    )
    nwbfile.add_stimulus_template(stimulus_template)

    nwbfile.intracellular_recordings.add_column(
        name="stimulus_template",
        data=[
            TimeSeriesReference(0, 5, stimulus_template),
            # (start_index, index_count, stimulus_template)
            TimeSeriesReference(1, 3, stimulus_template),
            TimeSeriesReference.empty(stimulus_template),
        ],
        # if there was no data for that recording, use empty reference
        description=(
            "Column storing the reference to the stimulus template for the recording (rows)."
        ),
        category="stimuli",
        col_cls=TimeSeriesReferenceVectorData,
    )

    icephys_simultaneous_recordings = nwbfile.get_icephys_simultaneous_recordings()
    icephys_simultaneous_recordings.add_column(
        name="simultaneous_recording_tag",
        description="A custom tag for simultaneous_recordings",
    )
    simultaneous_index = nwbfile.add_icephys_simultaneous_recording(
        recordings=[rowindex, rowindex2, rowindex3],
        id=12,
        simultaneous_recording_tag="LabTag1",
    )
    repetition_index = nwbfile.add_icephys_repetition(
        sequential_recordings=[simultaneous_index], id=17
    )
    nwbfile.add_icephys_experimental_condition(repetitions=[repetition_index], id=19)
    nwbfile.icephys_experimental_conditions.add_column(
        name="tag",
        data=np.arange(1),
        description="integer tag for a experimental condition",
    )
    return nwbfile


def _nwb_ca_imaging(nwbfile: NWBFile) -> NWBFile:
    """
    Calcium Imaging
    https://pynwb.readthedocs.io/en/latest/tutorials/domain/ophys.html
    """
    generator = np.random.default_rng()
    device = nwbfile.create_device(
        name="Microscope",
        description="My two-photon microscope",
        manufacturer="The best microscope manufacturer",
    )
    optical_channel = OpticalChannel(
        name="OpticalChannel",
        description="an optical channel",
        emission_lambda=500.0,
    )
    imaging_plane = nwbfile.create_imaging_plane(
        name="ImagingPlane",
        optical_channel=optical_channel,
        imaging_rate=30.0,
        description="a very interesting part of the brain",
        device=device,
        excitation_lambda=600.0,
        indicator="GFP",
        location="V1",
        grid_spacing=[0.01, 0.01],
        grid_spacing_unit="meters",
        origin_coords=[1.0, 2.0, 3.0],
        origin_coords_unit="meters",
    )
    one_p_series = OnePhotonSeries(
        name="OnePhotonSeries",
        description="Raw 1p data",
        data=np.ones((1000, 100, 100)),
        imaging_plane=imaging_plane,
        rate=1.0,
        unit="normalized amplitude",
    )
    nwbfile.add_acquisition(one_p_series)
    two_p_series = TwoPhotonSeries(
        name="TwoPhotonSeries",
        description="Raw 2p data",
        data=np.ones((1000, 100, 100)),
        imaging_plane=imaging_plane,
        rate=1.0,
        unit="normalized amplitude",
    )

    nwbfile.add_acquisition(two_p_series)

    corrected = ImageSeries(
        name="corrected",  # this must be named "corrected"
        description="A motion corrected image stack",
        data=np.ones((1000, 100, 100)),
        unit="na",
        format="raw",
        starting_time=0.0,
        rate=1.0,
    )

    xy_translation = TimeSeries(
        name="xy_translation",
        description="x,y translation in pixels",
        data=np.ones((1000, 2)),
        unit="pixels",
        starting_time=0.0,
        rate=1.0,
    )

    corrected_image_stack = CorrectedImageStack(
        corrected=corrected,
        original=one_p_series,
        xy_translation=xy_translation,
    )

    motion_correction = MotionCorrection(corrected_image_stacks=[corrected_image_stack])

    ophys_module = nwbfile.create_processing_module(
        name="ophys", description="optical physiology processed data"
    )

    ophys_module.add(motion_correction)

    img_seg = ImageSegmentation()

    ps = img_seg.create_plane_segmentation(
        name="PlaneSegmentation",
        description="output from segmenting my favorite imaging plane",
        imaging_plane=imaging_plane,
        reference_images=one_p_series,  # optional
    )

    ophys_module.add(img_seg)

    for _ in range(30):
        image_mask = np.zeros((100, 100))

        # randomly generate example image masks
        x = generator.integers(0, 95)
        y = generator.integers(0, 95)
        image_mask[x : x + 5, y : y + 5] = 1

        # add image mask to plane segmentation
        ps.add_roi(image_mask=image_mask)

    ps2 = img_seg.create_plane_segmentation(
        name="PlaneSegmentation2",
        description="output from segmenting my favorite imaging plane",
        imaging_plane=imaging_plane,
        reference_images=one_p_series,  # optional
    )

    for _ in range(30):
        # randomly generate example starting points for region
        x = generator.integers(0, 95)
        y = generator.integers(0, 95)

        # define an example 4 x 3 region of pixels of weight '1'
        pixel_mask = [(ix, iy, 1) for ix in range(x, x + 4) for iy in range(y, y + 3)]

        # add pixel mask to plane segmentation
        ps2.add_roi(pixel_mask=pixel_mask)

    ps3 = img_seg.create_plane_segmentation(
        name="PlaneSegmentation3",
        description="output from segmenting my favorite imaging plane",
        imaging_plane=imaging_plane,
        reference_images=one_p_series,  # optional
    )

    for _ in range(30):
        # randomly generate example starting points for region
        x = generator.integers(0, 95)
        y = generator.integers(0, 95)
        z = generator.integers(0, 15)

        # define an example 4 x 3 x 2 voxel region of weight '0.5'
        voxel_mask = []
        for ix, iy, iz in product(range(x, x + 4), range(y, y + 3), range(z, z + 2)):
            voxel_mask.append((ix, iy, iz, 0.5))

        # add voxel mask to plane segmentation
        ps3.add_roi(voxel_mask=voxel_mask)
    rt_region = ps.create_roi_table_region(region=[0, 1], description="the first of two ROIs")
    roi_resp_series = RoiResponseSeries(
        name="RoiResponseSeries",
        description="Fluorescence responses for two ROIs",
        data=np.ones((50, 2)),  # 50 samples, 2 ROIs
        rois=rt_region,
        unit="lumens",
        rate=30.0,
    )
    fl = Fluorescence(roi_response_series=roi_resp_series)
    ophys_module.add(fl)
    return nwbfile


@pytest.fixture(scope="session")
def nwb_file(tmp_output_dir, nwb_file_base, request: pytest.FixtureRequest) -> Path:
    """
    NWB File created with pynwb that uses all the weird language features

    Borrowing code from pynwb docs in one humonogous fixture function
    since there's not really a reason to
    """
    nwb_path = tmp_output_dir / "test_nwb.nwb"
    if nwb_path.exists() and not request.config.getoption('--clean'):
        return nwb_path

    nwbfile = nwb_file_base
    nwbfile = _nwb_timeseries(nwbfile)
    nwbfile = _nwb_position(nwbfile)
    nwbfile = _nwb_ecephys(nwbfile)
    nwbfile = _nwb_units(nwbfile)
    nwbfile = _nwb_icephys(nwbfile)

    with NWBHDF5IO(nwb_path, "w") as io:
        io.write(nwbfile)

    return nwb_path
