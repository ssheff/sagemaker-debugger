from tornasole.core.access_layer.s3handler import S3Handler, ListRequest
from tornasole.core.logger import get_logger


logger = get_logger()


# list_info will be a list of ListRequest objects. Returns list of lists of files for each request
def _list_s3_prefixes(list_info):
    files = S3Handler().list_prefixes(list_info)
    if len(files) == 1:
        files = files[0]
    return files


def list_s3_objects(bucket, prefix, start_after_key=None, delimiter=""):
    last_token = None
    if start_after_key is None:
        start_after_key = prefix
    req = ListRequest(Bucket=bucket, Prefix=prefix, StartAfter=start_after_key, Delimiter=delimiter)
    objects = _list_s3_prefixes([req])
    if len(objects) > 0:
        last_token = objects[-1]
    return objects, last_token


def parse_collection_files_from_s3_objects(s3_objects):
    collection_files = []
    import re

    regexp = re.compile(".+/(.+_collections.(json|ts))")
    for s3_object in s3_objects:
        match = re.match(regexp, s3_object)
        if match:
            collection_files.append(match.group(1))
    return collection_files
