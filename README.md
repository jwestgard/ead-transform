# ead-transform
<i>Batch application of regular expressions to transform EAD files.</i>

Original idea: Given a set of match and replacement patterns as a JSON file, the transformer will apply those transformations in series to the set of non-hidden files in a specified import directory.

Update: In practice, encoding of files needs to be sorted out first. Proposed strategy for encoding verification:

1. open file as binary, read file and decode from UTF-8 (strict).
2. if illegal characters are found:
  1. store contents decoded from UTF-8 as Python unicode object;
  2. open file, read, and decode from Windows-1252 (or Latin-1);
  3. compare result to UTF-8 version using difflib, and present differences to the user for verification;
  4. repeat as necessary until a valid decoded version is found.
