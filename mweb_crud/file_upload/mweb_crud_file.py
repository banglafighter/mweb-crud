from mw_common import DataUtil
from mw_file_content import FileUtil
from mweb import FileStorage
from ..common import MWebCRUDException
from ..common.mweb_crud_config import MWebCRUDConfig
from ..data_transfer import MWebBaseDTO, MWebDTO, MWebIDDTO, MWebDatedDTO
from ..data_transfer.dto import File
from ..file_upload import UploadFileName, UploadCustomizer


class MWebCRUDFile:

    def get_file_size(self, file_object: FileStorage, default=0):
        if file_object.content_length:
            return file_object.content_length
        try:
            current_position = file_object.tell()
            file_object.seek(0, 2)
            size = file_object.tell()
            file_object.seek(current_position)
            return size
        except (AttributeError, IOError):
            pass

        return default

    def is_valid_size(self, file_storage: FileStorage, field: File) -> bool:
        size = self.get_file_size(file_storage)
        size_in_kb = round(size / 1024, 4)
        if field.max_size_kb and size_in_kb > field.max_size_kb:
            return False
        return True

    def get_file_extension(self, filename):
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return "jpg"

    def allowed_file(self, filename, file_extensions: list):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in file_extensions

    def is_allowed_file_extension(self, file_storage: FileStorage, field: File) -> bool:
        if field.allowed_extensions and not self.allowed_file(file_storage.filename, field.allowed_extensions):
            return False
        return True

    def validate_files(self, data: dict, validator: MWebBaseDTO | MWebDTO | MWebIDDTO | MWebDatedDTO) -> dict:
        if validator is None:
            return data

        errors = {}
        for field_name in validator.fields:
            field = validator.fields[field_name]
            if isinstance(field, File):
                file_storage: FileStorage = DataUtil.dict_value(data, field_name)
                if file_storage and isinstance(file_storage, FileStorage):
                    if not self.is_valid_size(file_storage=file_storage, field=field):
                        errors[field_name] = MWebCRUDConfig.FILE_SIZE_NOT_MATCH_MSG
                    elif not self.is_allowed_file_extension(file_storage=file_storage, field=field):
                        errors[field_name] = MWebCRUDConfig.INVALID_FILE_EXTENSION_MSG
        if errors and len(errors):
            raise MWebCRUDException(message=MWebCRUDConfig.DATA_VALIDATION_ERROR_MSG, details=errors)
        return data

    def prepare_name(self, uuid: str, data: dict, validator: MWebBaseDTO | MWebDTO | MWebIDDTO | MWebDatedDTO, upload_customizer: UploadCustomizer) -> dict:
        file_name_map : dict = {}
        custom_file_name: list[UploadFileName] = []
        uuid = str(uuid)
        if upload_customizer is not None and upload_customizer.custom_file_name is not None:
            custom_file_name = upload_customizer.custom_file_name

        for upload_file_name in custom_file_name:
            file_name_map[upload_file_name.fieldName] = upload_file_name.filename

        for field_name in validator.fields:
            field = validator.fields[field_name]
            if isinstance(field, File) and field_name not in file_name_map:
                prefix = ""
                if field.save_prefix:
                    prefix = field.save_prefix + "-"
                file_name_map[field.name] = (prefix + uuid).lower()
        return file_name_map


    async def process_and_upload_files(self, request: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO, upload_path: str | None, data: dict, uuid: str, upload_customizer: UploadCustomizer | None = None, fsp : str | None = None):
        self.validate_files(data=data, validator=request)
        if upload_path is None:
            raise MWebCRUDException(message=MWebCRUDConfig.INVALID_FILE_UPLOAD_PATH_MSG)
        file_name_map = self.prepare_name(uuid=uuid, data=data, validator=request, upload_customizer=upload_customizer)

        upload_store_path: str = upload_path
        if fsp:
            upload_store_path = FileUtil.join_path(upload_path, fsp)

        FileUtil.create_directories(upload_store_path)
        for field_name in file_name_map:
            file_storage: FileStorage = DataUtil.dict_value(data=data, key=field_name)
            if file_storage and isinstance(file_storage, FileStorage):
                actual_file = file_storage.filename.lower()
                filename = f"{file_name_map[field_name]}.{self.get_file_extension(actual_file)}"
                if filename:
                    filename = filename.lower()

                if upload_customizer is None or not await upload_customizer.custom_upload(upload_path=upload_store_path, data=data, uuid=uuid, field=field_name, file_storage=file_storage):
                    file_upload_path = FileUtil.join_path(upload_store_path, filename)
                    FileUtil.delete(file_upload_path)
                    await file_storage.save(file_upload_path)
                    request.fields[field_name].is_uploaded = True
                    data[field_name] = filename
        return data
