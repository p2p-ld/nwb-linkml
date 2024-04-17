# Purpose

If [pynwb](https://pynwb.readthedocs.io/en/stable/) already exists,
why `nwb_linkml`?

Two kinds of reasons: 

- using NWB as a test case for a larger infrastructure project, and
- potentially improving the state of NWB itself.

## A Stepping Stone...

In the 
(word on how and why we are focusing on NWB as part of a larger project)

## Interoperable Schema Language

**We want to make NWB a seed format in an interoperable, peer-to-peer
graph of research data**

NWB is written with its own [{index}`schema language`](https://schema-language.readthedocs.io/en/latest/)
(And see [the next section](nwb) for more information). It seems to have been created
primarily because other schema languages at the time couldn't easily handle array
specifications with fine-grained control of numerical format and shape.

The schema language is now relatively stable and does what it's designed to do,
but it being a domain-specific language rather than a general one makes it very
difficult to use NWB data alongside other formats.

`nwb_linkml` translates NWB to [linkml](https://linkml.io/), a schema language
for declaring **{index}`Linked Data`** schema. Linked Data schema consist of
semantic triplets, rather than an object hierarchy, and can make use of
**controlled vocabularies** to reuse terms and classes from other
schemas and ontologies.

## Storage Format Flexibility

**We want to use NWB in lots of different ways**

NWB as a format is designed with the intention for use with multiple
storage backends, but patterns and features of HDF5 have made their way
into the schema and the schema language, making direct translation to
other storage systems difficult. This is a problem for practical usage of
NWB data, since HDF5 files don't lend themselves to querying across many
files - eg. to find datasets that have some common piece of metadata, one
would have to download them all in full first. Having a whole hierarchy of
data in a single file is convenient in some ways, but this also makes them
difficult to share or split between computers which is a common need
when collecting data across multiple instruments and computers. 

NWB, currently, lends itself towards being an **archival** format --- where
data is converted as a last step before publishing --- rather than a
**experimental** or **computational** format that can be used as a convenient
container of heterogeneous data during collection and analysis.

The LinkML team has also made a large number of [generators](https://linkml.io/linkml/generators/index.html)
to convert LinkML schema to different formats, including JSON Schema, GraphQL, SPARQL,
SQL/SQLAlchemy, and {mod}`~nwb_linkml.generators.pydantic`. 

Since we have to use LinkML in a somewhat nonstandard way to accommodate
NWB's arrays, references, and naming conventions, these generators won't be
immediately available for use, but with some minor modification we should
be able to get NWB out of HDF5 files and into other formats.

## Zero-code Schema Extensions

**We want every researcher and every tool to have their own schemas.**

pynwb makes use of NWB Schema internally, but [schema extensions](https://pynwb.readthedocs.io/en/stable/tutorials/general/extensions.html#sphx-glr-tutorials-general-extensions-py)
require a decent amount of adjoining code to use. The underlying hdmf library
is relatively complex, and so to use a schema extension one must also 
program the python classes or mappings to python class attributes
needed to use them, configuration for getter and setter methods,
i/o routines, etc. Since schema extensions are relatively hard to make,
to accommodate heterogeneous data NWB uses `DynamicTable`s, which can be
given arbitrary new columns.

The loose coupling between schema and code has a few impacts:
- Many labs end up with their own independent software
  library for converting their data into NWB
- Interoperability and meta-analysis suffer because terms are defined 
  ad-hoc and with little discoverability.
- Linking and versioning schema is hard, as the schema language doesn't 
  support it, and the code needs to be kept in-sync with the schema
- It's hard for tool-builders to implement direct export to NWB while
  maintaining flexibility in their libraries

Instead by making all models directly generated from schema, and by
making use of pydantic and other validation and metaprogramming tools,
we want to make it possible for every experiment to have its own schema
extension. We want to make experimental data part of the normal social
process of sharing results --- translation: we want to be able to
put our work in conversation with other related work!

## Pythonic API

**We want NWB to be as simple to use as a python dataclass.**

We think there is room for improvement in NWB's API:

`````{tab-set}
````{tab-item} pynwb
From the ndx-miniscope extension:

The extension code is intended to be used like this:

```python
from pynwb import NWBFile, NWBHDF5IO
from pynwb.image import ImageSeries
from natsort import natsorted

from ndx_miniscope.utils import (
    add_miniscope_device,
    get_starting_frames,
    get_timestamps,
    read_miniscope_config,
    read_notes,
)

nwbfile = NWBFile(...)

# Load the miscroscope settings
miniscope_folder_path = "C6-J588_Disc5/15_03_28/Miniscope/"
miniscope_metadata = read_miniscope_config(folder_path=miniscope_folder_path)
# Create the Miniscope device with the microscope metadata and add it to NWB
add_miniscope_device(nwbfile=nwbfile, device_metadata=miniscope_metadata)

# Load the behavioral camera settings
behavcam_folder_path = "C6-J588_Disc5/15_03_28/BehavCam_2/"
behavcam_metadata = read_miniscope_config(folder_path=behavcam_folder_path)
# Create the Miniscope device with the behavioral camera metadata and add it to NWB
add_miniscope_device(nwbfile=nwbfile, device_metadata=behavcam_metadata)

save_path = os.path.join(folder_path, "test_out.nwb")
with NWBHDF5IO(save_path, "w") as io:
    io.write(nwbfile)

```

That uses these underlying functions to handle validation, 
coercion, and add to the NWB file:

```python
def add_miniscope_device(nwbfile: NWBFile, device_metadata: dict) -> NWBFile:
    """
    Adds a Miniscope device based on provided metadata.
    Can be used to add device for the microscope and the behavioral camera.

    Parameters
    ----------
    nwbfile : NWBFile
        The nwbfile to add the Miniscope device to.
    device_metadata: dict
        The metadata for the device to be added.

    Returns
    -------
    NWBFile
        The NWBFile passed as an input with the Miniscope added.

    """
    device_metadata_copy = deepcopy(device_metadata)
    assert "name" in device_metadata_copy, "'name' is missing from metadata."
    device_name = device_metadata_copy["name"]
    if device_name in nwbfile.devices:
        return nwbfile

    roi = device_metadata_copy.pop("ROI", None)
    if roi:
        device_metadata_copy.update(ROI=[roi["height"], roi["width"]])

    device = Miniscope(**device_metadata_copy)
    nwbfile.add_device(device)

    return nwbfile

def add_miniscope_image_series(
    nwbfile: NWBFile,
    metadata: dict,
    timestamps: np.ndarray,
    image_series_index: int = 0,
    external_files: Optional[List[str]] = None,
    starting_frames: Optional[List[int]] = None,
) -> NWBFile:
    """
    Adds an ImageSeries with a linked Miniscope device based on provided metadata.
    The metadata for the device to be linked should be stored in metadata["Behavior]["Device"].

    Parameters
    ----------
    nwbfile : NWBFile
        The nwbfile to add the image series to.
    metadata: DeepDict
        The metadata storing the necessary metadata for creating the image series and linking it to the appropriate device.
    timestamps : np.ndarray
        The timestamps for the behavior movie source.
    image_series_index : int, optional
        The metadata for ImageSeries is a list of the different image series to add.
        Specify which element of the list with this parameter.
    external_files : List[str], optional
        List of external files associated with the ImageSeries.
    starting_frames :  List[int], optional
        List of starting frames for each external file.

    Returns
    -------
    NWBFile
        The NWBFile passed as an input with the ImageSeries added.

    """
    assert "Behavior" in metadata, "The metadata for ImageSeries and Device should be stored in 'Behavior'."
    assert (
        "ImageSeries" in metadata["Behavior"]
    ), "The metadata for ImageSeries should be stored in metadata['Behavior']['ImageSeries']."
    assert (
        "Device" in metadata["Behavior"]
    ), "The metadata for Device should be stored in metadata['Behavior']['Device']."
    image_series_kwargs = deepcopy(metadata["Behavior"]["ImageSeries"][image_series_index])
    image_series_name = image_series_kwargs["name"]

    if image_series_name in nwbfile.acquisition:
        return nwbfile

    # Add linked device to ImageSeries
    device_metadata = metadata["Behavior"]["Device"][image_series_index]
    device_name = device_metadata["name"]
    if device_name not in nwbfile.devices:
        add_miniscope_device(nwbfile=nwbfile, device_metadata=device_metadata)
    device = nwbfile.get_device(name=device_name)
    image_series_kwargs.update(device=device)

    assert external_files, "'external_files' must be specified."
    if starting_frames is None and len(external_files) == 1:
        starting_frames = [0]
    assert len(starting_frames) == len(
        external_files
    ), "The number of external files must match the length of 'starting_frame'."
    image_series_kwargs.update(
        format="external",
        external_file=external_files,
        starting_frame=starting_frames,
        timestamps=H5DataIO(timestamps, compression=True),
    )

    image_series = ImageSeries(**image_series_kwargs)
    nwbfile.add_acquisition(image_series)

```
````
````{tab-item} nwb_linkml
An example of how we want `nwb_linkml` to work.

There are no additional underlying classes or functions to be written,
since the pydantic models are directly generated from the schema extension,
and `to` and `from` methods are generic for different types of 
input data (json files, videos). Tool developers can distribute
NWB schema that map 1:1 to their output formats, decreasing the need
for conversion code. 

```python
from pathlib import Path
from nwb_linkml.models.miniscope import Miniscope
from nwb_linkml.models.core import ImageSeries, NWBFile

# Load data for miniscope and videos
miniscope = Miniscope.from_json('config.json')
videos = []
for video_path in Path('./my_data/').glob('*.avi'):
    video = ImageSeries.from_video(video_path)
    video.device = miniscope
    videos.append(video)
    
# add to file
file = NWBFile.from_hdf('my_data.nwb')
file.devices['my_miniscope'] = miniscope
file.acquisition['my_videos'] = videos
file.save()
```

````



`````
