class MWebCRUDConfig:
    # API Config
    PAGE_PARAM_NAME: str = "page"
    ITEM_PER_PAGE_PARAM_NAME: str = "per-page"
    SEARCH_FIELD_PARAM_NAME: str = "search"
    TOTAL_ITEM_PER_PAGE: int = 25
    SORT_FIELD_PARAM_NAME: str = "sort-field"
    SORT_ORDER_PARAM_NAME: str = "sort-order"
    SORT_DEFAULT_ORDER_NAME: str = "desc"
    SORT_DEFAULT_FIELD_NAME: str = "id"

    # Swagger UI Config
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_SWAGGER_AUTH: bool = False
    SWAGGER_AUTH_USERNAME: str = "mweb"
    SWAGGER_AUTH_PASSWORD: str = "mweb12"
    SWAGGER_JSON_URL: str = "/swagger-json"
    SWAGGER_UI_URL: str = "/swagger-ui"
    SWAGGER_UI_ASSETS_URL: str = "/swagger-assets"
    SWAGGER_DEFAULT_TAG_NAME: str = "Common"
    SWAGGER_TITLE: str = "MWeb Swagger"
    SWAGGER_APP_VERSION: str = "1.0.0"

    ENABLED_JWT_AUTH: bool = True



    # Display Messages
    CREATE_SUCCESS_MSG: str = "Created successfully"
    DELETE_SUCCESS_MSG = "Deleted successfully"
    FAILED_TO_DELETE_RECORD_MSG = "Failed to delete record"
    UPDATE_SUCCESS_MSG = "Updated successfully"
    INVALID_INPUT_DATA_MSG = "Invalid input data"
    FAILED_TO_SAVE_DATA_MSG = "Failed to save data"
    FAILED_TO_UPDATE_DATA_MSG = "Failed to update data"

    INVALID_JSON_REQUEST_DATA_MSG = "Invalid JSON request data"
    DATA_VALIDATION_ERROR_MSG = "Data validation error!"
    RECORD_NOT_FOUND_MSG = "Record not found"
    ID_REQUIRED_MSG = "The ID field is required"
    UUID_REQUIRED_MSG = "The UUID field is required"
    VALUE_ALREADY_EXISTS_MSG = "This value already exists"
    DUPLICATE_ENTRY_ERROR_MSG = "Duplicate entry detected"
    RECORD_ID_OR_UUID_REQUIRED_MSG = "Record ID or UUID is required"
    DTO_IS_REQUIRED_MSG = "DTO is required"

    UNKNOWN_ERROR_MSG: str = "Unknown Error Occurred!"
    FILE_SIZE_NOT_MATCH_MSG = "File size exceeds the allowed limit"
    INVALID_FILE_EXTENSION_MSG = "Invalid file type uploaded"
    INVALID_FILE_UPLOAD_PATH_MSG = "Invalid file upload path"

