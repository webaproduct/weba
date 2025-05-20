# TODO: improve this exception
#  (many types of error for many fields with custom messages)
class CRNDVsdCreateDataListError(Exception):
    """
    current version:
    field_name_list - list of required fields

    future version:
    fields - dict with lists as value
    """
    def __init__(self, message, field_name_list: list):
        super().__init__(message)
        self.field_name_list = field_name_list
