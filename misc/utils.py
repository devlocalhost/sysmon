# TODO: this needs to be loaded using the config file
CONVERSION_TYPE = 1024

def to_bytes(kilobytes):
    """convert kilobytes to bytes"""

    return kilobytes * 1024


def convert_bytes(fsize, units=("bytes", "KiB", "MiB", "GiB", "TiB")):
    """convert bytes to human readable format"""

    for unit in units:
        if fsize < CONVERSION_TYPE:
            return f"{fsize:.2f} {unit if CONVERSION_TYPE == 1024 else unit.replace('i', '')}"

        fsize /= CONVERSION_TYPE

    return f"{fsize:.2f} {units[-1]}"
