from uuid import UUID


class GUID(UUID):
    @classmethod
    def of(cls, guid: str) -> 'GUID':
        return GUID(guid)
