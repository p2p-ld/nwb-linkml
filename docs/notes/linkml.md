# LinkML

Features of LinkML to keep in mind while writing the schema.


- [Defining slots](https://linkml.io/linkml/schemas/advanced.html#defining-slots) - slots that
  can be used to infer class identity - would be useful for inferring types in all the recursive
  shit
- [multidimensional arrays](https://linkml.io/linkml/howtos/multidimensional-arrays.html)
- [units](https://linkml.io/linkml-model/docs/unit/)
  - See also [modeling measurements](https://linkml.io/linkml/howtos/model-measurements.html)
- modeling conditional presence https://github.com/linkml/linkml-model/issues/126


## Python dataclass problems

- Generator doesn't seem to honor the `slot_usage` property - eg. for the `Schema` class,
  `doc` is marked as required despite the requirement being removed