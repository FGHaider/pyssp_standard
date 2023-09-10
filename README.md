# pyssp_standard
[<img src="https://img.shields.io/badge/Status-In Development-orange.svg?logo=LOGO">](<LINK>)

Python package to interact with files specified by the SSP standard [<img src="https://img.shields.io/badge/SSP-Standard-blue.svg?logo=LOGO">](<https://ssp-standard.org/>)
. The library allows for 
the creation, reading and editing of SSV, SSM and SSB files. In addition, it allows for the reading of SSP, FMU and SSD
files. The intended use is for pre-processing work and inspection of a given file.

In addition to the SSP standard the SRMD standard is also supported.

## Documentation
Here follows a number of examples of how to use the library.


### SSV 

#### Example
Here a ssv file is opened and checked if it is compliant with the SSP standard.

```python
with SSV(file_path) as file:
    file.check_compliance()
```


### SSM

#### Example
Here a ssm file is opened and checked if it is compliant with the SSP standard.

```python
with SSM(file_path) as file:
    file.check_compliance()
```


### FMU

In your SSP there are often FMU:s (functional mockup units) that hold the binaries for the models. pyssp unpacks these 
when loading an SSP or alternatively loading them directly, allowing the user to peak into its contents, specifically 
to see all declared ScalarVariables and lookup them on the basis of causality or variability.

#### Example

```python
with FMU(file_path) as file:
    parameters = file.get(causality='Parameter')
    print(Parameters)
```
with the print out formatted as:
```
___________________________________________________________________________________________
               Name: pipeC.tao_Tfrict
        Description: Time constant in LP-filtering of Text
        Variability: tunable
          Causality: parameter
 ```

### SRMD
Below follows an example where an SRMD file is created, coupled to some data and then added to an SSP file.
```python
test_file = Path('./test.srmd')
data_file = Path('./doc/embrace/test.csv')
def test_create_srmd(write_file):
    with SRMD(write_file, 'w') as file:
        classification = Classification(classification_type='test')
        classification.add_classification_entry(ClassificationEntry('test', 'This is a test'))
        file.add_classification(classification)
        file.assign_data(data_file)
        
with SSP(test_file) as file:
    file.add_resource(test_file)
    file.add_resource(data_file)
```
