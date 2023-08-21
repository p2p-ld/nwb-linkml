# nwb-schema-language

Translation of the nwb-schema-language to LinkML

## Website

[https://p2p_ld.github.io/nwb-schema-language](https://p2p_ld.github.io/nwb-schema-language)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [nwb_schema_language](src/nwb_schema_language)
    * [schema](src/nwb_schema_language/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/nwb_schema_language/datamodel) -- generated
      Python datamodel
* [tests/](tests/) - Python tests

## Developer Documentation

<details>
Use the `make` command to generate project artefacts:

* `make all`: make everything
* `make deploy`: deploys site
</details>

## Credits

This project was made with
[linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter).
