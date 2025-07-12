from dataclasses import dataclass
from mweb import FileStorage
from mweb_crud.data_transfer.dto import File


@dataclass
class UploadFileName:
    fieldName: str
    filename: str


class UploadCustomizer:
    custom_file_name: list[UploadFileName] | None = None

    def add_name(self, field_name: str, filename: str):
        if self.custom_file_name is None:
            self.custom_file_name = []
        self.custom_file_name.append(UploadFileName(field_name, filename))
        return self

    async def custom_upload(self, upload_path: str, data: dict, uuid: str, field: File, file_storage: FileStorage) -> bool:
        return False
