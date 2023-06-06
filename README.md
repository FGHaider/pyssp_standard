# pyssp
Python library to interact with files specified by the SSP standard (https://ssp-standard.org/). The libary allows for 
the creation, reading and editing of SSV, SSM and SSB files. In addition, it allows for the reading of SSP, FMU and SSD
files. The intended use is for pre-processing work and inspection of a given file.

## Examples
Here follows a number of examples of how to use the library.

### SSV 

Here a ssv file is opened and checked whether is it is compliance with SSP standard.

```
with SSV(file_path) as ssv
    ssv.check_compliance()
```
