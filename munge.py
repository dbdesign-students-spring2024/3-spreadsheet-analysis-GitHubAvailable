# place your code to clean up the data file below.

"""
munge.py - clean up data files (i.e., discard 0 market cap companies, 
fill empty cells with "unknown" as data of each stock is assumed to be 
independent from others).
"""

import csv
import re
import os.path
import warnings
from typing import Callable
from typing import overload

    
def write_csv(
    destination: str, 
    data: list[list[str]], 
    *, 
    encoding: str = "utf-8", 
    overwrite: bool = False
) -> None: 
    """
    Write data to given directory as CSV file.

    Parameters
    ----------
    destination : str, path to where data to be saved, a URL, default ``""``
        String, the parsed data will be written to desired. If empty, 
        return the parsed data. Create a file if it does not exist. 
    data : list of list of str
        A list of string lists with each of them representing a row of the 
        CSV file (the first row is the header).
    encoding : str, default utf-8
        String, the encoding the data should use.
    overwrite : bool, default ``False``.
        Boolean, overwrite the destination file if true. Otherwise, 
        raise ``FileExistsError``.

    Raises
    ------
    FileExistsError : if the file specified ``destination`` already exists and
        ``overwrite`` is ``False``.
    """
    # Check if can write.
    if not overwrite and os.path.isfile(path=destination):
        raise FileExistsError(f"{destination} already exists")
    
    # Write to destination.
    with open(destination, "w", encoding=encoding) as file:
        for row in data:
            file.write(",".join(row) + "\n")


def _is_postive_integer(x : int) -> bool:
    """Return if input is positive integer."""
    return type(x) == int and x > 0

def _is_positive(entry : str) -> bool:
    try:
        return float(entry) > 0
    except Exception:
        return False

def _filter_row(row : list[str], 
                old_header : dict[str : list[int]], 
                repetitive_keys : list[int], 
                merge_duplicate : bool = False):
    """
    Remove repeated column of a CSV value.
    
    Parameters
    ----------
    row : list[str], a CSV row
        List of strings, one row of a CSV file.
    old_header : dict[str : int], the header of the CSV
        Dictionary of string keys with integer indices. Stores the indices 
        where a key appeared.
    repetitive_key : list[int], list containing indices of repetitive
    keys
        List of integers. Stores the index of keys for 
        its repeated occurences (i.e., its 2nd, 3rd ... occurences).
    merge_duplicate : bool, optional, whether columns with the same keys 
    should be merged.
        Boolean, concatenate values of identical keys in the same order of 
        their column index at the first occurence. Default is `False`.
    """
    if merge_duplicate:
        for key in old_header:
            if len(key) == 1:
                continue

            # Concatenate values
            first = key[0]
            for index in range(1, len(key), 1):
                row[first] += row[index]

    # Remove duplicate columns
    for index in repetitive_keys[::-1]:
        row.remove(row[index])


def munge_csv(path : str, 
              *, 
              start : int = 1,
              end : int = -1, 
              encoding : str = "utf-8", 
              req_keys : dict[str : Callable[[str], bool]] = dict(), 
              default_fill : dict[str, any] = dict(), 
              fix : bool = False, 
              merge_duplicate : bool = False) -> list[list[str]]:
    """
    Clean up a csv file at a given directory and return cleaned data.
    Remove columns with repetitive keys.

    Parameters
    ----------
    path : str, path to the data, a URL
        String, the directory of the file. For example, 
        ``ocean_temp_data.fwf``.
    start: int, optional, begining line of the actual data
        The line number of the first line (excluding the header) 
        of the data to be read. Default is 1.
    end: int | None, optional, last line of the actual data
        The line number of the last line of the data to be read. 
        Read to the end if set to `None`.
        Default is -1.
    encoding : str, default utf-8
        String, the encoding the file used.
    req_keys : dict[str : Callable[[str], bool]], dict of keys that 
    requires valid data
        A dict contains function to check if value for specific key is valid.
        Rows with invalid value will be discarded.
    default_fill : dict[str, any], dict of default value for specified keys
        A dict of default value for specified keys, filled when for empty value
        or problemetic ones if `fix` is `True`.
    fix : bool, optional, whether invalid value should be fixed.
        Boolean, replace invalid value with default if its key in 
        `default_fill`. Discard the row if no default found. 
        Default is `False`.
    merge_duplicate : bool, optional, whether columns with the same keys 
    should be merged.
        Boolean, concatenate values of identical keys in the same order of 
        their column index at the first occurence. Default is `False`.
    
    Returns
    -------
    list[list[str]] 
        Return a list with the each element is 
        a list representing a row of the original header and data extracted
        (the first row is the header and all other rows are rows of data).

    Raises
    ------
    ValueError : if one or more inputs invalid.
    FileNotFoundError : if source file specified by ``path`` does not exist.
    """
    if not _is_postive_integer(start):
        raise ValueError(f"'start' ({start}) must be a positive integer")
    if end != -1 and not _is_postive_integer(end):
        raise ValueError(f"Bounded 'end' ({end}) must be a positive integer")
    if end != -1 and start > end:
        raise ValueError(f"'start' ({start}) must be less than or "
                         + f"equal to bounded 'end' ({end})")

    # Setup containers.
    # Make a map from key to column index.
    filtered_header: dict[str : int]
    lines: list[str] = []

    # Read data.
    with open(path, "r", encoding=encoding) as file:
        # Read header
        head = file.readline()[:-1].split(",")
        if len(head) == 0:
            raise KeyError(f"Header cannot be empty, but found '{head}'")
        lines.append(head)

        # Create dict of repetitive keys and repetitive columns.
        old_header: dict[str : list[int]] = dict()
        filtered_header = dict()
        repetitive_index = []

        # Setup old_header and new_header.
        for (index, key) in enumerate(head):
            if key not in old_header:
                old_header[key] = []
            else:
                # Mark row, to be removed
                repetitive_index.append(index)
            old_header[key].append(index)
            filtered_header[key] = len(filtered_header)

        # Skip unneeded lines.
        for _ in range(start - 1):
            file.readline()
        
        # Set current line number.
        cur_line = start

        # Set parsing flags.
        invalid_word = False
        
        # Parse data
        while cur_line != end:
            line: str = file.readline()
            row = line[:-1].split(",")

            # Check if keys missing
            if len(row) < len(filtered_header):
                # Skip empty rows.
                if line.strip() != "":
                    error_msg = f"Line {cur_line} length less than " \
                                + f"the header. Expected " \
                                + f" {len(filtered_header)}, got {len(row)}"
                    raise ValueError(error_msg)
                
                # Reach end of file.
                if not line or line[-1] != "\n":
                    # No `+1` since `cur_line` is not a record.
                    print(f"Munge finished. Original range " \
                          + f"{cur_line - start} records. Munged data " \
                          + f"{len(lines) - 1} records.")
                    return lines
                
                warn_msg = f"Line {cur_line} is empty, dropped."
                warnings.warn(warn_msg, RuntimeWarning)
                cur_line += 1
                continue

            # Remove repetitive keys
            _filter_row(row, old_header, repetitive_index, merge_duplicate)

            # Check if the row is still unvalid
            if len(row) > len(head):
                warn_msg = f"Line {cur_line} has extra data," \
                           + f"dropped. Expected {len(head)}," \
                           + f" got{len(row)}"
                warnings.warn(warn_msg, RuntimeWarning)
                cur_line += 1
                continue

            cur_line += 1

            # Check if required data is valid, fix if needed.
            for (key, is_valid) in req_keys.items():
                # Get index or the given key.
                index = filtered_header[key]

                # Determine if the row should be kept.
                if is_valid(row[index]):
                    continue
                if not fix or key not in default_fill:
                    invalid_word = True
                    break
                
                # Fix invalid data.
                row[index] = default_fill[key]
            
            if invalid_word:
                invalid_word = False
                continue

            # Fill in default value.
            for key in default_fill:
                # Get index or the given key.
                index = filtered_header[key]

                if row[index] == "":
                    row[index] = default_fill[key]

            lines.append(row)
    
    print(f"Munge finished. Original range " \
          + f"{cur_line - start + 1} records. Munged data " \
          + f"{len(lines) - 1} records.")
    return lines
    

def main():
    # Set parameters.
    encoding = 'utf-8'

    # Set file directory.
    root = os.path.dirname(__file__)
    data_path = os.path.join(root, "data/nasdaq_screener_20240206.csv")
    target_path = os.path.join(root, "data/clean_data.csv")

    cleaned_data = munge_csv(data_path, encoding=encoding, 
                             req_keys={"Market Cap" : _is_positive}, 
                             default_fill={"IPO Year" : "Unknown", 
                                           "Country" : "Unknown", 
                                           "Sector" : "Unknown", 
                                           "Industry" : "Unknown"})
    write_csv(target_path, cleaned_data, 
              encoding=encoding, overwrite=True)
    

if __name__ == "__main__":
    main()