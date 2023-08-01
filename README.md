# pyssp_standard
[<img src="https://img.shields.io/badge/Status-In Development-orange.svg?logo=LOGO">](<LINK>)

Python pacakge to interact with files specified by the SSP standard [<img src="https://img.shields.io/badge/SSP-Standard-blue.svg?logo=LOGO">](<https://ssp-standard.org/>)
. The libary allows for 
the creation, reading and editing of SSV, SSM and SSB files. In addition, it allows for the reading of SSP, FMU and SSD
files. The intended use is for pre-processing work and inspection of a given file.

The package is currently in alpha, this means:
- There will be bugs
- The API may change radically, as a result documentation is lacking
- Only a limited set of features have been implemented
- License may change

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
