import py3exiv2bind
from uiucprescon import imagevalidate
from . import AbsProfile


class HathiJP2(AbsProfile):
    """HathiTrust JPEG2000 submission file requirements

        JP2 Metadata

        +----------------------------+---------------------------+---------+
        + Tag                        | Value                     | Checked |
        +============================+===========================+=========+
        | CompressionScheme          | JPEG-2000                 | No      |
        +----------------------------+---------------------------+---------+
        | Format                     | JPEG-2000                 | No      |
        +----------------------------+---------------------------+---------+
        | MIMETYPE                   | image/jp2                 | No      |
        +----------------------------+---------------------------+---------+
        | Brand (or "MajorBrand")    | jp2                       | No      |
        +----------------------------+---------------------------+---------+
        | MinorVersion               | 0                         | No      |
        +----------------------------+---------------------------+---------+
        | Compatibility              | jp2                       | No      |
        | (or "CompatibleBrands")    |                           |         |
        +----------------------------+---------------------------+---------+
        | Xsize (or "ImageWidth")    | matches                   | No      |
        |                            | XMP/tiff:imageWidth       |         |
        +----------------------------+---------------------------+---------+
        | Ysize (or "ImageHeight")   | matches                   | No      |
        |                            | XMP/tiff:imageHeight      |         |
        +----------------------------+---------------------------+---------+
        | NumberOfLayers             | mandatory, but no         | No      |
        |                            | required value            |         |
        +----------------------------+---------------------------+---------+
        | NumberDecompositionLevels  | mandatory, but no         | No      |
        |                            | required value            |         |
        +----------------------------+---------------------------+---------+
        | BitsPerSample              | 8 for Grayscale,          | No      |
        |                            | (8,8,8 [24-bit]) for      |         |
        |                            | sRGB                      |         |
        +----------------------------+---------------------------+---------+
        | XSamplingFrequency         | generally between         | No      |
        |                            | 300/1 and 600/1,          |         |
        |                            | matches                   |         |
        |                            | XMP/tiff:Xresolution      |         |
        +----------------------------+---------------------------+---------+
        | YSamplingFrequency         | generally between         | No      |
        |                            | 300/1 and 600/1,          |         |
        |                            | matches                   |         |
        |                            | XMP/tiff:Yresolution      |         |
        +----------------------------+---------------------------+---------+
        | SamplingFrequencyUnit      | mandatory, matches        | No      |
        |                            | XMP/SamplingFrequencyUnit |         |
        +----------------------------+---------------------------+---------+


        XMP Metadata

        +--------------------------------+---------------------------+---------+
        | Tag                            | Value                     | Checked |
        +================================+===========================+=========+
        | xpacket field                  | W5M0MpCehiHzreSzNTczkc9d  | No      |
        +--------------------------------+---------------------------+---------+
        | tiff:imageWidth                | matches JP2/Xsize         | No      |
        +--------------------------------+---------------------------+---------+
        | tiff:imageHeight               | matches JP2/Ysize         | No      |
        +--------------------------------+---------------------------+---------+
        | tiff:BitsPerSample             | 8 for Grayscale,          | No      |
        |                                | (8,8,8 [24-bit])          |         |
        |                                | for sRGB                  |         |
        +--------------------------------+---------------------------+---------+
        | tiff:Compression               | 34712 (=JPEG2000)         | No      |
        +--------------------------------+---------------------------+---------+
        | tiff:PhotometricInterpretation | 2 for sRGG, 1 for         | No      |
        |                                | Grayscale                 |         |
        +--------------------------------+---------------------------+---------+
        | tiff:Orientation               | 1                         | No      |
        |                                | (Horizontal/Normal)       |         |
        +--------------------------------+---------------------------+---------+
        | tiff:SamplesPerPixel           | 3 for sRGB, 1 for         | No      |
        |                                | Grayscale                 |         |
        +--------------------------------+---------------------------+---------+
        | tiff:Xresolution               | generally between         | No      |
        |                                | 300/1 and 600/1,          |         |
        |                                | matches JP2/XSize         |         |
        +--------------------------------+---------------------------+---------+
        | tiff:Yresolution               | generally between         | No      |
        |                                | 300/1 and 600/1,          |         |
        |                                | matches JP2/YSize         |         |
        +--------------------------------+---------------------------+---------+
        | SamplingFrequencyUnit          | mandatory, matches        | No      |
        |                                | JP2/SamplingFrequencyUnit |         |
        +--------------------------------+---------------------------+---------+
        | tiff:ResolutionUnit            | 2 (inches)                | No      |
        +--------------------------------+---------------------------+---------+
        | dc:source                      | object $id/$filename      | No      |
        +--------------------------------+---------------------------+---------+
        | tiff:DateTime                  | formatted                 | No      |
        |                                | YYYY:mm:ddTHH:MM:SS,      |         |
        |                                | for example               |         |
        |                                | 2010:05:24T13:45:30       |         |
        +--------------------------------+---------------------------+---------+
        | tiff:Artist                    | University of             | No      |
        |                                | Illinois at               |         |
        |                                | Urbana-Champaign          |         |
        |                                | Library                   |         |
        +--------------------------------+---------------------------+---------+
        | tiff:Make                      | make of                   | No      |
        |                                | camera/scanner            |         |
        +--------------------------------+---------------------------+---------+
        | tiff:Model                     | model of camera/scanner   | No      |
        +--------------------------------+---------------------------+---------+

    Note:
        Data pulled from the `Digitized Book Requirements`_.

    .. _Digitized Book Requirements:
       https://wiki.illinois.edu/wiki/display/LibraryDigitalPreservation/Digitized+Book+Requirements
    """
    def validate(self, file: str) -> imagevalidate.Report:
        report = imagevalidate.Report()
        image = py3exiv2bind.Image(file)
        # report._properties['']
        return report
