from distutils.core import setup

setup(
    name='pyssp_standard',
    packages=['pyssp_standard'],
    version='0.5',
    license='MIT',
    description='Simple python package for reading, modifying and creating files, specified in the SSP Standard',
    long_description='',
    long_description_content_type='text/markdown',
    author='Fredrik Haider',
    author_email='',
    url='https://github.com/FGHaider/pyssp',
    download_url='https://github.com/FGHaider/pyssp/archive/refs/tags/v_01.tar.gz',
    keywords=['SSP', 'system', 'engineering'],
    install_requires=[
        'lxml',
        'xmlschema',
        'pytest',
        'pint',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
